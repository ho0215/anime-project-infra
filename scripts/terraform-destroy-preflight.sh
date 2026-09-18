#!/usr/bin/env bash
# terraform destroy 직전: TF 밖 잔여물 + DELETE_FAILED 노드그룹을 정리한다.
# 증상 (CD destroy 실패):
#   - EKS nodegroup DELETE_FAILED / AccessDenied (노드 Access Entry 없음)
#   - subnet/IGW DependencyViolation + "mapped public address(es)"
#     → Ingress ALB(ENI·퍼블릭 IP)가 TF state 밖에 남음
#
#   CLUSTER=aniverse-eks PROJECT=aniverse ./scripts/terraform-destroy-preflight.sh
set -euo pipefail

REGION="${AWS_REGION:-ap-northeast-2}"
CLUSTER="${EKS_CLUSTER_NAME:-aniverse-eks}"
PROJECT="${PROJECT_NAME:-aniverse}"
NODEGROUP="${EKS_NODEGROUP_NAME:-${PROJECT}-nodes}"
NODE_ROLE_NAME="${EKS_NODE_ROLE_NAME:-${PROJECT}-eks-node-role}"
WAIT_SEC="${DESTROY_PREFLIGHT_WAIT_SEC:-900}"

need() { command -v "$1" >/dev/null || { echo "$1 필요" >&2; exit 1; }; }
need aws

account="$(aws sts get-caller-identity --query Account --output text)"
node_role_arn="arn:aws:iam::${account}:role/${NODE_ROLE_NAME}"

echo "==> preflight destroy (cluster=${CLUSTER} region=${REGION})"

cluster_exists=0
if aws eks describe-cluster --region "${REGION}" --name "${CLUSTER}" >/dev/null 2>&1; then
  cluster_exists=1
fi

# ---- 1) 노드 EC2_LINUX Access Entry 보장 (노드그룹 삭제/drain 용) ----
if [ "${cluster_exists}" = 1 ]; then
  echo "==> ensure EC2_LINUX access entry for ${node_role_arn}"
  if ! aws eks describe-access-entry \
    --region "${REGION}" \
    --cluster-name "${CLUSTER}" \
    --principal-arn "${node_role_arn}" >/dev/null 2>&1; then
    aws eks create-access-entry \
      --region "${REGION}" \
      --cluster-name "${CLUSTER}" \
      --principal-arn "${node_role_arn}" \
      --type EC2_LINUX \
      --output text \
      --query 'accessEntry.principalArn' || true
  else
    echo "    access entry already present"
  fi
fi

# ---- 2) Ingress ALB (LB Controller 가 만든 TF 밖 LB) 삭제 ----
# 태그: elbv2.k8s.aws/cluster=<cluster>
echo "==> delete orphan ALBs tagged elbv2.k8s.aws/cluster=${CLUSTER}"
mapfile -t ALB_ARNS < <(
  aws elbv2 describe-load-balancers --region "${REGION}" \
    --query 'LoadBalancers[].LoadBalancerArn' --output text 2>/dev/null \
    | tr '\t' '\n' | sed '/^$/d' || true
)
for arn in "${ALB_ARNS[@]:-}"; do
  [ -n "${arn}" ] || continue
  tags="$(aws elbv2 describe-tags --region "${REGION}" --resource-arns "${arn}" \
    --query "TagDescriptions[0].Tags[?Key=='elbv2.k8s.aws/cluster'].Value | [0]" \
    --output text 2>/dev/null || echo None)"
  name="$(aws elbv2 describe-load-balancers --region "${REGION}" --load-balancer-arns "${arn}" \
    --query 'LoadBalancers[0].LoadBalancerName' --output text 2>/dev/null || echo '?')"
  if [ "${tags}" = "${CLUSTER}" ] || [[ "${name}" == k8s-"${PROJECT}"-* ]]; then
    echo "    delete ALB ${name}"
    aws elbv2 delete-load-balancer --region "${REGION}" --load-balancer-arn "${arn}" || true
  fi
done

# Target groups left by controller
echo "==> delete orphan target groups tagged elbv2.k8s.aws/cluster=${CLUSTER}"
mapfile -t TG_ARNS < <(
  aws elbv2 describe-target-groups --region "${REGION}" \
    --query 'TargetGroups[].TargetGroupArn' --output text 2>/dev/null \
    | tr '\t' '\n' | sed '/^$/d' || true
)
for arn in "${TG_ARNS[@]:-}"; do
  [ -n "${arn}" ] || continue
  tags="$(aws elbv2 describe-tags --region "${REGION}" --resource-arns "${arn}" \
    --query "TagDescriptions[0].Tags[?Key=='elbv2.k8s.aws/cluster'].Value | [0]" \
    --output text 2>/dev/null || echo None)"
  if [ "${tags}" = "${CLUSTER}" ]; then
    echo "    delete TG ${arn}"
    aws elbv2 delete-target-group --region "${REGION}" --target-group-arn "${arn}" || true
  fi
done

# ---- 3) DELETE_FAILED / 잔여 노드그룹 강제 정리 ----
# 핵심: EKS 노드그룹 삭제는 ASG 의 ReplaceUnhealthy 가 *재개* 되어 있어야 함.
# (suspend 해 두면 AutoScalingGroupInvalidConfiguration 으로 DELETE_FAILED)
# ASG 0 + terminate → resume ReplaceUnhealthy → delete-nodegroup → CFN FORCE.
list_nodegroup_asgs() {
  local asgs
  asgs="$(aws eks describe-nodegroup \
    --region "${REGION}" \
    --cluster-name "${CLUSTER}" \
    --nodegroup-name "${NODEGROUP}" \
    --query 'nodegroup.resources.autoScalingGroups[].name' \
    --output text 2>/dev/null || true)"
  if [ -z "${asgs}" ] || [ "${asgs}" = "None" ]; then
    asgs="$(aws autoscaling describe-auto-scaling-groups --region "${REGION}" \
      --query "AutoScalingGroups[?contains(AutoScalingGroupName, '${NODEGROUP}')].AutoScalingGroupName" \
      --output text 2>/dev/null || true)"
  fi
  echo "${asgs}"
}

force_scale_nodegroup_asg() {
  local asgs
  asgs="$(list_nodegroup_asgs)"
  for asg in ${asgs}; do
    [ -n "${asg}" ] || continue
    echo "    force ASG ${asg} → min/desired/max=0 (Launch only suspended)"
    # ReplaceUnhealthy 는 절대 suspend 하지 않음 — EKS delete-nodegroup 이 요구함
    aws autoscaling suspend-processes --region "${REGION}" --auto-scaling-group-name "${asg}" \
      --scaling-processes Launch AZRebalance AlarmNotification ScheduledActions 2>/dev/null || true
    mapfile -t ids < <(
      aws autoscaling describe-auto-scaling-groups --region "${REGION}" \
        --auto-scaling-group-names "${asg}" \
        --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text 2>/dev/null \
        | tr '\t' '\n' | sed '/^$/d' || true
    )
    for id in "${ids[@]:-}"; do
      [ -n "${id}" ] || continue
      aws autoscaling set-instance-protection --region "${REGION}" \
        --auto-scaling-group-name "${asg}" --instance-ids "${id}" \
        --no-protected-from-scale-in 2>/dev/null || true
    done
    aws autoscaling update-auto-scaling-group --region "${REGION}" \
      --auto-scaling-group-name "${asg}" \
      --min-size 0 --desired-capacity 0 --max-size 0 || true
    for id in "${ids[@]:-}"; do
      [ -n "${id}" ] || continue
      echo "    terminate ${id}"
      aws ec2 terminate-instances --region "${REGION}" --instance-ids "${id}" >/dev/null 2>&1 || true
    done
  done
}

resume_nodegroup_asg_for_delete() {
  local asgs
  asgs="$(list_nodegroup_asgs)"
  for asg in ${asgs}; do
    [ -n "${asg}" ] || continue
    echo "    resume ASG processes (esp. ReplaceUnhealthy) on ${asg}"
    aws autoscaling resume-processes --region "${REGION}" \
      --auto-scaling-group-name "${asg}" 2>/dev/null || true
    # 명시적으로 ReplaceUnhealthy 재개
    aws autoscaling resume-processes --region "${REGION}" \
      --auto-scaling-group-name "${asg}" \
      --scaling-processes ReplaceUnhealthy Launch 2>/dev/null || true
  done
}

force_delete_nodegroup_cfn() {
  local asgs stack
  asgs="$(list_nodegroup_asgs)"
  echo "    resolve CFN stacks from ASG physical ids"
  for asg in ${asgs}; do
    [ -n "${asg}" ] || continue
    stack="$(aws cloudformation describe-stack-resources --region "${REGION}" \
      --physical-resource-id "${asg}" \
      --query 'StackResources[0].StackName' --output text 2>/dev/null || echo None)"
    if [ -z "${stack}" ] || [ "${stack}" = "None" ]; then
      # 이름 힌트: ASG eks-aniverse-nodes-<uuid> → 동일 prefix 스택 탐색
      stack="$(aws cloudformation list-stacks --region "${REGION}" \
        --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE UPDATE_ROLLBACK_COMPLETE \
          DELETE_FAILED UPDATE_ROLLBACK_FAILED ROLLBACK_COMPLETE DELETE_IN_PROGRESS \
        --query "StackSummaries[?contains(StackName, '${NODEGROUP}')].StackName | [0]" \
        --output text 2>/dev/null || echo None)"
    fi
    if [ -z "${stack}" ] || [ "${stack}" = "None" ]; then
      echo "    no CFN stack for ASG ${asg}"
      continue
    fi
    echo "    delete-stack FORCE ${stack} (from ASG ${asg})"
    aws cloudformation delete-stack --region "${REGION}" \
      --stack-name "${stack}" \
      --deletion-mode FORCE_DELETE_STACK 2>/dev/null \
      || aws cloudformation delete-stack --region "${REGION}" --stack-name "${stack}" 2>/dev/null \
      || true
    echo "    wait stack delete ${stack}"
    aws cloudformation wait stack-delete-complete --region "${REGION}" --stack-name "${stack}" 2>/dev/null || true
  done
}

try_delete_nodegroup() {
  resume_nodegroup_asg_for_delete
  echo "    delete-nodegroup ${NODEGROUP}"
  aws eks delete-nodegroup \
    --region "${REGION}" \
    --cluster-name "${CLUSTER}" \
    --nodegroup-name "${NODEGROUP}" >/dev/null 2>&1 || true
}

if [ "${cluster_exists}" = 1 ]; then
  ng_status="$(aws eks describe-nodegroup \
    --region "${REGION}" \
    --cluster-name "${CLUSTER}" \
    --nodegroup-name "${NODEGROUP}" \
    --query 'nodegroup.status' --output text 2>/dev/null || echo MISSING)"
  echo "==> nodegroup ${NODEGROUP} status=${ng_status}"
  if [ "${ng_status}" != "MISSING" ] && [ "${ng_status}" != "None" ]; then
    aws eks describe-nodegroup \
      --region "${REGION}" \
      --cluster-name "${CLUSTER}" \
      --nodegroup-name "${NODEGROUP}" \
      --query 'nodegroup.health.issues' --output json 2>/dev/null || true

    force_scale_nodegroup_asg
    # 노드 IAM 롤이 이미 지워졌을 수 있음 — Access Entry 는 best-effort
    aws eks create-access-entry \
      --region "${REGION}" \
      --cluster-name "${CLUSTER}" \
      --principal-arn "${node_role_arn}" \
      --type EC2_LINUX >/dev/null 2>&1 || true
    try_delete_nodegroup

    echo "    wait nodegroup deleted (timeout ${WAIT_SEC}s)"
    deadline=$((SECONDS + WAIT_SEC))
    failed_rounds=0
    while (( SECONDS < deadline )); do
      st="$(aws eks describe-nodegroup \
        --region "${REGION}" \
        --cluster-name "${CLUSTER}" \
        --nodegroup-name "${NODEGROUP}" \
        --query 'nodegroup.status' --output text 2>/dev/null || echo MISSING)"
      if [ "${st}" = "MISSING" ] || [ "${st}" = "None" ]; then
        echo "    nodegroup gone"
        break
      fi
      if [ "${st}" = "DELETE_FAILED" ]; then
        failed_rounds=$((failed_rounds + 1))
        echo "    DELETE_FAILED (round ${failed_rounds}) — resume ASG + CFN force"
        force_scale_nodegroup_asg
        resume_nodegroup_asg_for_delete
        force_delete_nodegroup_cfn
        aws eks create-access-entry \
          --region "${REGION}" \
          --cluster-name "${CLUSTER}" \
          --principal-arn "${node_role_arn}" \
          --type EC2_LINUX >/dev/null 2>&1 || true
        try_delete_nodegroup
        if (( failed_rounds >= 3 )); then
          echo "ERROR: nodegroup still DELETE_FAILED after CFN force — aborting preflight" >&2
          aws eks describe-nodegroup \
            --region "${REGION}" \
            --cluster-name "${CLUSTER}" \
            --nodegroup-name "${NODEGROUP}" \
            --query 'nodegroup.health.issues' --output json >&2 || true
          exit 1
        fi
      fi
      sleep 20
    done
    # 최종 확인
    st="$(aws eks describe-nodegroup \
      --region "${REGION}" \
      --cluster-name "${CLUSTER}" \
      --nodegroup-name "${NODEGROUP}" \
      --query 'nodegroup.status' --output text 2>/dev/null || echo MISSING)"
    if [ "${st}" != "MISSING" ] && [ "${st}" != "None" ]; then
      echo "ERROR: nodegroup still present (${st}) — cluster destroy would fail with ResourceInUse" >&2
      exit 1
    fi
  fi
fi

# VPC id (cluster or Name tag)
VPC_ID=""
if [ "${cluster_exists}" = 1 ]; then
  VPC_ID="$(aws eks describe-cluster --region "${REGION}" --name "${CLUSTER}" \
    --query 'cluster.resourcesVpcConfig.vpcId' --output text 2>/dev/null || true)"
fi
if [ -z "${VPC_ID}" ] || [ "${VPC_ID}" = "None" ]; then
  VPC_ID="$(aws ec2 describe-vpcs --region "${REGION}" \
    --filters "Name=tag:Name,Values=${PROJECT}-vpc" \
    --query 'Vpcs[0].VpcId' --output text 2>/dev/null || true)"
fi
if [ -z "${VPC_ID}" ] || [ "${VPC_ID}" = "None" ]; then
  echo "==> no VPC found — skip EIP/ENI cleanup"
  echo "OK preflight (partial)"
  exit 0
fi
echo "==> VPC ${VPC_ID}"

# ---- 4) 퍼블릭 IP 매핑 해제 (IGW detach 차단 해제) ----
echo "==> disassociate/release EIPs in VPC"
mapfile -t ASSOCS < <(
  aws ec2 describe-addresses --region "${REGION}" \
    --filters "Name=domain,Values=vpc" \
    --query "Addresses[?NetworkInterfaceId!=null].[AssociationId,AllocationId,NetworkInterfaceId]" \
    --output text 2>/dev/null | tr '\t' ' ' || true
)
for line in "${ASSOCS[@]:-}"; do
  [ -n "${line}" ] || continue
  assoc="$(echo "${line}" | awk '{print $1}')"
  alloc="$(echo "${line}" | awk '{print $2}')"
  eni="$(echo "${line}" | awk '{print $3}')"
  eni_vpc="$(aws ec2 describe-network-interfaces --region "${REGION}" \
    --network-interface-ids "${eni}" \
    --query 'NetworkInterfaces[0].VpcId' --output text 2>/dev/null || echo None)"
  if [ "${eni_vpc}" != "${VPC_ID}" ]; then
    continue
  fi
  echo "    disassociate ${assoc} (eni=${eni})"
  aws ec2 disassociate-address --region "${REGION}" --association-id "${assoc}" || true
  # NAT/임시 EIP 만 release — 다른 프로젝트 EIP 는 건드리지 않음 (이 VPC ENI 만)
  if [ -n "${alloc}" ] && [ "${alloc}" != "None" ]; then
    echo "    release ${alloc}"
    aws ec2 release-address --region "${REGION}" --allocation-id "${alloc}" || true
  fi
done

# 인스턴스에 붙은 public IP 는 EIP 가 아닐 수 있음 → NAT/잔여 EC2 terminate 는 TF 에 맡기되,
# DELETE_FAILED 노드 인스턴스가 남았으면 강제 종료
echo "==> terminate leftover EC2 in VPC tagged kubernetes:cluster-name / ${PROJECT}"
mapfile -t INSTANCES < <(
  aws ec2 describe-instances --region "${REGION}" \
    --filters "Name=vpc-id,Values=${VPC_ID}" \
      "Name=instance-state-name,Values=pending,running,stopping,stopped" \
    --query 'Reservations[].Instances[].InstanceId' --output text 2>/dev/null \
    | tr '\t' '\n' | sed '/^$/d' || true
)
# 노드/NAT 만 — 이름 태그로 좁힘
for id in "${INSTANCES[@]:-}"; do
  [ -n "${id}" ] || continue
  name="$(aws ec2 describe-instances --region "${REGION}" --instance-ids "${id}" \
    --query 'Reservations[0].Instances[0].Tags[?Key==`Name`].Value|[0]' --output text 2>/dev/null || echo)"
  eks_tag="$(aws ec2 describe-instances --region "${REGION}" --instance-ids "${id}" \
    --query "Reservations[0].Instances[0].Tags[?Key=='eks:cluster-name'].Value|[0]" \
    --output text 2>/dev/null || echo)"
  if [ "${eks_tag}" = "${CLUSTER}" ] || [[ "${name}" == "${PROJECT}"* ]]; then
    echo "    terminate ${id} (Name=${name})"
    aws ec2 terminate-instances --region "${REGION}" --instance-ids "${id}" >/dev/null || true
  fi
done

# ---- 5) VPC 의존성 정리 (VPC destroy 가 수십 분 hang 하는 주원인) ----
# EKS 클러스터 삭제 직후 Hyperplane/ENI 가 비동기로 남음 → DeleteVpc 가 오래 걸리거나 DependencyViolation.
# available ENI 삭제 + (가능하면) non-default SG / VPC endpoint 제거. in-use 는 AWS 해제까지 대기.
echo "==> wait/clean ENIs + endpoints in VPC (EKS leftovers)"
eni_deadline=$((SECONDS + "${DESTROY_ENI_WAIT_SEC:-600}"))
while (( SECONDS < eni_deadline )); do
  mapfile -t ENI_ROWS < <(
    aws ec2 describe-network-interfaces --region "${REGION}" \
      --filters "Name=vpc-id,Values=${VPC_ID}" \
      --query 'NetworkInterfaces[].[NetworkInterfaceId,Status,InterfaceType,Description]' \
      --output text 2>/dev/null || true
  )
  avail=0
  inuse=0
  for row in "${ENI_ROWS[@]:-}"; do
    [ -n "${row}" ] || continue
    eni="$(echo "${row}" | awk '{print $1}')"
    st="$(echo "${row}" | awk '{print $2}')"
    itype="$(echo "${row}" | awk '{print $3}')"
    desc="$(echo "${row}" | cut -f4- | tr '\t' ' ')"
    if [ "${st}" = "available" ]; then
      avail=$((avail + 1))
      echo "    delete ENI ${eni} (${itype}: ${desc})"
      aws ec2 delete-network-interface --region "${REGION}" --network-interface-id "${eni}" || true
    else
      inuse=$((inuse + 1))
      echo "    in-use ENI ${eni} (${itype}: ${desc}) — waiting for AWS release"
    fi
  done
  # VPC endpoints (Interface type) 도 ENI 를 붙잡음
  mapfile -t VPCE < <(
    aws ec2 describe-vpc-endpoints --region "${REGION}" \
      --filters "Name=vpc-id,Values=${VPC_ID}" \
      --query 'VpcEndpoints[].VpcEndpointId' --output text 2>/dev/null \
      | tr '\t' '\n' | sed '/^$/d' || true
  )
  for ep in "${VPCE[@]:-}"; do
    [ -n "${ep}" ] || continue
    echo "    delete vpc-endpoint ${ep}"
    aws ec2 delete-vpc-endpoints --region "${REGION}" --vpc-endpoint-ids "${ep}" || true
  done

  if (( avail == 0 && inuse == 0 )); then
    echo "    VPC has no ENIs"
    break
  fi
  # available 는 방금 삭제 시도함. in-use 만 남으면 AWS Hyperplane 해제 대기.
  sleep 15
done

echo "==> delete non-default security groups in VPC (best-effort)"
mapfile -t SGS < <(
  aws ec2 describe-security-groups --region "${REGION}" \
    --filters "Name=vpc-id,Values=${VPC_ID}" \
    --query 'SecurityGroups[?GroupName!=`default`].GroupId' --output text 2>/dev/null \
    | tr '\t' '\n' | sed '/^$/d' || true
)
for pass in 1 2 3; do
  left=0
  for sg in "${SGS[@]:-}"; do
    [ -n "${sg}" ] || continue
    if aws ec2 delete-security-group --region "${REGION}" --group-id "${sg}" 2>/dev/null; then
      echo "    deleted SG ${sg}"
    else
      left=$((left + 1))
    fi
  done
  (( left == 0 )) && break
  sleep 5
done

# 남은 ENI 요약 (VPC hang 진단용)
echo "==> remaining ENIs in VPC (if any, DeleteVpc will keep retrying)"
aws ec2 describe-network-interfaces --region "${REGION}" \
  --filters "Name=vpc-id,Values=${VPC_ID}" \
  --query 'NetworkInterfaces[].[NetworkInterfaceId,Status,Description]' \
  --output table 2>/dev/null || true

echo "OK preflight"

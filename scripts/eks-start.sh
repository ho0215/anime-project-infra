#!/usr/bin/env bash
# EKS 비용 절약: 워커 + NAT 끄기/켜기 (컨트롤 플레인은 유지 → 약 $0.10/h)
#
# 사용:
#   export EKS_CLUSTER_NAME=aniverse-eks
#   export EKS_NODEGROUP_NAME=aniverse-nodes
#   ./scripts/eks-stop.sh   # 워커 desired=0 + ASG 강제 0 + NAT stop
#   ./scripts/eks-start.sh  # NAT start → ASG resume → 워커 복구
#   ./scripts/eks-status.sh
#
# 완전 삭제: Terraform destroy — docs/eks-start-stop.md
set -euo pipefail

REGION="${AWS_REGION:-ap-northeast-2}"
CLUSTER="${EKS_CLUSTER_NAME:-aniverse-eks}"
NODEGROUPS="${EKS_NODEGROUP_NAME:-aniverse-nodes}"
DESIRED="${EKS_DESIRED_SIZE:-2}"
MIN_START="${EKS_MIN_SIZE:-0}"
# EKS API: maxSize 최소 1 (0 불가)
MAX_SIZE="${EKS_MAX_SIZE:-4}"
MAX_STOP="${EKS_MAX_SIZE_STOP:-1}"
WAIT_NODES="${EKS_WAIT_NODES:-1}"
WAIT_TIMEOUT="${EKS_WAIT_TIMEOUT_SEC:-600}"
# Terraform modules/nat Name 태그
NAT_NAME="${EKS_NAT_NAME:-aniverse-nat-instance}"
# stop 후 ASG 인스턴스 0 대기
WAIT_ASG_EMPTY="${EKS_WAIT_ASG_EMPTY:-1}"

ASG_SUSPEND_PROCS="Launch ReplaceUnhealthy AZRebalance AlarmNotification ScheduledActions"

need_aws() {
  command -v aws >/dev/null || { echo "aws CLI 필요" >&2; exit 1; }
}

list_ngs() {
  # shellcheck disable=SC2086
  for ng in ${NODEGROUPS}; do
    echo "${ng}"
  done
}

asg_name_for_ng() {
  local ng="$1"
  aws eks describe-nodegroup \
    --region "${REGION}" \
    --cluster-name "${CLUSTER}" \
    --nodegroup-name "${ng}" \
    --query 'nodegroup.resources.autoScalingGroups[0].name' \
    --output text
}

suspend_asg() {
  local asg="$1"
  echo "==> ASG suspend (${asg}): ${ASG_SUSPEND_PROCS}"
  # shellcheck disable=SC2086
  aws autoscaling suspend-processes \
    --region "${REGION}" \
    --auto-scaling-group-name "${asg}" \
    --scaling-processes ${ASG_SUSPEND_PROCS}
}

resume_asg() {
  local asg="$1"
  echo "==> ASG resume (${asg})"
  aws autoscaling resume-processes \
    --region "${REGION}" \
    --auto-scaling-group-name "${asg}"
}

set_asg_desired() {
  local asg="$1" desired="$2"
  echo "==> ASG set-desired-capacity (${asg}) → ${desired}"
  # scale-in protection 있으면 종료가 막힘
  local ids
  ids="$(aws autoscaling describe-auto-scaling-groups --region "${REGION}" \
    --auto-scaling-group-names "${asg}" \
    --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text | tr '\t' ' ')"
  if [ -n "${ids}" ]; then
    echo "==> clear scale-in protection: ${ids}"
    # shellcheck disable=SC2086
    aws autoscaling set-instance-protection --region "${REGION}" \
      --auto-scaling-group-name "${asg}" \
      --instance-ids ${ids} \
      --no-protected-from-scale-in || true
  fi
  aws autoscaling set-desired-capacity \
    --region "${REGION}" \
    --auto-scaling-group-name "${asg}" \
    --desired-capacity "${desired}"
}

asg_running_count() {
  local asg="$1"
  aws autoscaling describe-auto-scaling-groups \
    --region "${REGION}" \
    --auto-scaling-group-names "${asg}" \
    --query 'length(AutoScalingGroups[0].Instances[?LifecycleState==`InService` || LifecycleState==`Pending` || LifecycleState==`Terminating`])' \
    --output text 2>/dev/null || echo "0"
}

wait_asg_empty() {
  local asg="$1"
  [ "${WAIT_ASG_EMPTY}" = "1" ] || return 0
  echo "==> waiting for ASG ${asg} instances → 0 (timeout ${WAIT_TIMEOUT}s)"
  local deadline=$((SECONDS + WAIT_TIMEOUT))
  while (( SECONDS < deadline )); do
    local n
    n="$(asg_running_count "${asg}")"
    echo "  instances=${n}"
    if [ "${n}" = "0" ] || [ "${n}" = "None" ]; then
      echo "OK — ASG empty"
      return 0
    fi
    sleep 15
  done
  echo "ERROR: ASG still has instances after ${WAIT_TIMEOUT}s" >&2
  aws autoscaling describe-auto-scaling-groups --region "${REGION}" \
    --auto-scaling-group-names "${asg}" \
    --query 'AutoScalingGroups[0].{Desired:DesiredCapacity,Instances:Instances[].{Id:InstanceId,State:LifecycleState}}' \
    --output json >&2 || true
  return 1
}

scale_ng() {
  local ng="$1" min="$2" max="$3" desired="$4"
  echo "==> ${CLUSTER}/${ng}: min=${min} max=${max} desired=${desired}"
  aws eks update-nodegroup-config \
    --region "${REGION}" \
    --cluster-name "${CLUSTER}" \
    --nodegroup-name "${ng}" \
    --scaling-config "minSize=${min},maxSize=${max},desiredSize=${desired}" \
    --output text --query 'update.id'
}

wait_ng_active() {
  local ng="$1"
  echo "==> wait nodegroup ${ng} ACTIVE"
  local i
  for i in $(seq 1 60); do
    local st
    st="$(aws eks describe-nodegroup --region "${REGION}" \
      --cluster-name "${CLUSTER}" --nodegroup-name "${ng}" \
      --query 'nodegroup.status' --output text)"
    echo "  [$i] status=${st}"
    if [ "${st}" = "ACTIVE" ]; then
      return 0
    fi
    sleep 5
  done
  echo "WARN: nodegroup not ACTIVE yet" >&2
  return 0
}

find_nat_ids() {
  # Name 태그 + (옵션) instance id
  if [ -n "${EKS_NAT_INSTANCE_ID:-}" ]; then
    echo "${EKS_NAT_INSTANCE_ID}"
    return 0
  fi
  aws ec2 describe-instances \
    --region "${REGION}" \
    --filters \
      "Name=tag:Name,Values=${NAT_NAME}" \
      "Name=instance-state-name,Values=pending,running,stopping,stopped" \
    --query 'Reservations[].Instances[].InstanceId' \
    --output text
}

nat_state() {
  local id="$1"
  aws ec2 describe-instances --region "${REGION}" --instance-ids "${id}" \
    --query 'Reservations[0].Instances[0].State.Name' --output text
}

stop_nat() {
  local ids
  ids="$(find_nat_ids | tr '\t' ' ' | xargs || true)"
  if [ -z "${ids}" ]; then
    echo "WARN: NAT (${NAT_NAME}) not found — skip" >&2
    return 0
  fi
  echo "==> stop NAT: ${ids}"
  # shellcheck disable=SC2086
  aws ec2 stop-instances --region "${REGION}" --instance-ids ${ids} --output text \
    --query 'StoppingInstances[].{Id:InstanceId,Prev:PreviousState.Name,Cur:CurrentState.Name}'
  local id
  for id in ${ids}; do
    echo "==> wait NAT ${id} stopped"
    aws ec2 wait instance-stopped --region "${REGION}" --instance-ids "${id}"
    echo "OK — NAT ${id} $(nat_state "${id}")"
  done
}

start_nat() {
  local ids
  ids="$(find_nat_ids | tr '\t' ' ' | xargs || true)"
  if [ -z "${ids}" ]; then
    echo "ERROR: NAT (${NAT_NAME}) not found — cannot start workers without egress" >&2
    return 1
  fi
  echo "==> start NAT: ${ids}"
  # shellcheck disable=SC2086
  aws ec2 start-instances --region "${REGION}" --instance-ids ${ids} --output text \
    --query 'StartingInstances[].{Id:InstanceId,Prev:PreviousState.Name,Cur:CurrentState.Name}'
  local id
  for id in ${ids}; do
    echo "==> wait NAT ${id} running"
    aws ec2 wait instance-running --region "${REGION}" --instance-ids "${id}"
    # source/dest check 는 Terraform 이 false — stop/start 후에도 유지됨
    echo "OK — NAT ${id} $(nat_state "${id}")"
  done
  # iptables NAT 규칙이 user_data 로만 들어가면 재부팅 후 복구됨(AMI 설정). 잠깐 대기.
  sleep 20
}

wait_nodes_ready() {
  [ "${WAIT_NODES}" = "1" ] || return 0
  if ! command -v kubectl >/dev/null; then
    echo "kubectl 없음 — Ready 대기 스킵. kubeconfig: aws eks update-kubeconfig --name ${CLUSTER}"
    return 0
  fi
  echo "==> waiting for ${DESIRED} node(s) Ready (timeout ${WAIT_TIMEOUT}s)"
  local deadline=$((SECONDS + WAIT_TIMEOUT))
  while (( SECONDS < deadline )); do
    local ready
    ready="$(kubectl get nodes --no-headers 2>/dev/null | awk '$2 ~ /^Ready/ {c++} END {print c+0}')"
    if [ "${ready}" -ge "${DESIRED}" ]; then
      echo "OK — ${ready} node(s) Ready"
      kubectl get nodes -o wide 2>/dev/null || true
      return 0
    fi
    echo "  ready=${ready}/${DESIRED} ..."
    sleep 15
  done
  echo "WARN: timeout waiting for nodes — ./scripts/eks-status.sh 로 확인" >&2
  return 0
}

cmd="$(basename "$0")"
need_aws

case "${cmd}" in
  eks-stop.sh)
    echo "Stopping workers + NAT on ${CLUSTER} (control plane stays UP ~\$0.10/h)"
    for ng in $(list_ngs); do
      asg="$(asg_name_for_ng "${ng}")"
      if [ -z "${asg}" ] || [ "${asg}" = "None" ]; then
        echo "ERROR: ASG not found for ${ng}" >&2
        exit 1
      fi
      suspend_asg "${asg}"
      # EKS desired=0 (maxSize API 최소 1)
      scale_ng "${ng}" 0 "${MAX_STOP}" 0 || true
      wait_ng_active "${ng}"
      # EKS 반영이 느리면 ASG 를 직접 0 — 실제 EC2 종료의 핵심
      set_asg_desired "${asg}" 0
      wait_asg_empty "${asg}"
    done
    stop_nat
    echo "OK — workers gone, NAT stopped. 남는 비용 ≈ EKS 컨트롤 플레인 \$0.10/h (+ EBS)."
    echo "EC2 Running: 비어 있어야 함. Check: ./scripts/eks-status.sh"
    ;;
  eks-start.sh)
    echo "Starting NAT then workers on ${CLUSTER} (desired=${DESIRED}, max=${MAX_SIZE})"
    start_nat
    for ng in $(list_ngs); do
      asg="$(asg_name_for_ng "${ng}")"
      if [ -z "${asg}" ] || [ "${asg}" = "None" ]; then
        echo "ERROR: ASG not found for ${ng}" >&2
        exit 1
      fi
      resume_asg "${asg}"
      scale_ng "${ng}" "${MIN_START}" "${MAX_SIZE}" "${DESIRED}"
      wait_ng_active "${ng}"
    done
    wait_nodes_ready
    echo "OK — curl -sI https://aniverse.my/health/"
    ;;
  eks-status.sh)
    echo "Cluster: ${CLUSTER} (${REGION})"
    aws eks describe-cluster --region "${REGION}" --name "${CLUSTER}" \
      --query 'cluster.{status:status,version:version,endpoint:endpoint}' --output table || true
    echo
    for ng in $(list_ngs); do
      echo "--- nodegroup ${ng} ---"
      aws eks describe-nodegroup --region "${REGION}" --cluster-name "${CLUSTER}" --nodegroup-name "${ng}" \
        --query 'nodegroup.{status:status,scaling:scalingConfig}' --output table || true
      asg="$(asg_name_for_ng "${ng}" 2>/dev/null || true)"
      if [ -n "${asg}" ] && [ "${asg}" != "None" ]; then
        echo "ASG: ${asg}"
        aws autoscaling describe-auto-scaling-groups --region "${REGION}" \
          --auto-scaling-group-names "${asg}" \
          --query 'AutoScalingGroups[0].{Desired:DesiredCapacity,Min:MinSize,Max:MaxSize,Suspended:SuspendedProcesses[].ProcessName,Instances:Instances[].{Id:InstanceId,State:LifecycleState}}' \
          --output json || true
      fi
    done
    echo
    echo "--- NAT (${NAT_NAME}) ---"
    ids="$(find_nat_ids | tr '\t' ' ' || true)"
    if [ -z "${ids}" ]; then
      echo "(not found)"
    else
      for id in ${ids}; do
        echo "${id}: $(nat_state "${id}")"
      done
    fi
    echo
    echo "비용: 노드·NAT off 여도 EKS 컨트롤 플레인 ≈ \$0.10/h. 완전 끄기: terraform destroy (keep-dns)."
    ;;
  *)
    echo "unknown command: ${cmd}" >&2
    exit 1
    ;;
esac

#!/usr/bin/env bash
# EKS 비용 절약: 워커 노드만 끄기/켜기 (컨트롤 플레인은 유지 → 약 $0.10/h)
#
# 사용:
#   export EKS_CLUSTER_NAME=aniverse-eks
#   export EKS_NODEGROUP_NAME=aniverse-nodes   # 여러 개면 공백 구분
#   ./scripts/eks-stop.sh     # desired=0 + ASG Launch suspend (Autoscaler 재기동 방지)
#   ./scripts/eks-start.sh    # ASG resume + desired 복구 + Ready 대기
#   ./scripts/eks-status.sh
#
# 완전 삭제(컨트롤 플레인 비용까지 0)는 Terraform destroy — docs/eks-start-stop.md
# Route53 존은 destroy 해도 유지: scripts/terraform-destroy-keep-dns.sh
set -euo pipefail

REGION="${AWS_REGION:-ap-northeast-2}"
CLUSTER="${EKS_CLUSTER_NAME:-aniverse-eks}"
NODEGROUPS="${EKS_NODEGROUP_NAME:-aniverse-nodes}"
DESIRED="${EKS_DESIRED_SIZE:-2}"
MIN_START="${EKS_MIN_SIZE:-0}"
# EKS API: maxSize 최소 1 (0 불가). stop 때는 1로 두고 ASG Launch 를 suspend.
MAX_SIZE="${EKS_MAX_SIZE:-4}"
MAX_STOP="${EKS_MAX_SIZE_STOP:-1}"
# start 후 노드 Ready 대기 (0=끄기)
WAIT_NODES="${EKS_WAIT_NODES:-1}"
WAIT_TIMEOUT="${EKS_WAIT_TIMEOUT_SEC:-600}"

# Cluster Autoscaler / ASG 가 desired=0 을 되돌리지 못하게 Launch 등 suspend
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
    echo "Stopping workers on ${CLUSTER} (control plane stays UP ~\$0.10/h)"
    echo "NOTE: EKS maxSize 최소 1 → max=${MAX_STOP}; ASG Launch suspend 로 Autoscaler 재기동 방지"
    for ng in $(list_ngs); do
      asg="$(asg_name_for_ng "${ng}")"
      if [ -z "${asg}" ] || [ "${asg}" = "None" ]; then
        echo "WARN: ASG not found for ${ng} — scale only" >&2
      else
        suspend_asg "${asg}"
      fi
      # maxSize=0 은 EKS API 가 거절함 (valid min 1)
      scale_ng "${ng}" 0 "${MAX_STOP}" 0
    done
    echo "OK — nodes scaling to 0 (desired=0, ASG Launch suspended). NAT 인스턴스는 유지."
    echo "EC2 콘솔: Running 필터만 보면 워커는 수 분 내 사라지고 NAT 1대만 남음."
    echo "Check: ./scripts/eks-status.sh"
    ;;
  eks-start.sh)
    echo "Starting workers on ${CLUSTER} (desired=${DESIRED}, max=${MAX_SIZE})"
    for ng in $(list_ngs); do
      asg="$(asg_name_for_ng "${ng}")"
      if [ -n "${asg}" ] && [ "${asg}" != "None" ]; then
        resume_asg "${asg}"
      fi
      scale_ng "${ng}" "${MIN_START}" "${MAX_SIZE}" "${DESIRED}"
    done
    wait_nodes_ready
    echo "OK — curl -sI http://aniverse.my/health/  (helm 앱이 이미 있으면 바로 접속)"
    ;;
  eks-status.sh)
    echo "Cluster: ${CLUSTER} (${REGION})"
    aws eks describe-cluster --region "${REGION}" --name "${CLUSTER}" \
      --query 'cluster.{status:status,version:version,endpoint:endpoint}' --output table || true
    echo
    aws eks list-nodegroups --region "${REGION}" --cluster-name "${CLUSTER}" --output text || true
    echo
    for ng in $(list_ngs); do
      echo "--- nodegroup ${ng} ---"
      aws eks describe-nodegroup --region "${REGION}" --cluster-name "${CLUSTER}" --nodegroup-name "${ng}" \
        --query 'nodegroup.{status:status,scaling:scalingConfig,instanceTypes:instanceTypes}' --output table || true
      asg="$(asg_name_for_ng "${ng}" 2>/dev/null || true)"
      if [ -n "${asg}" ] && [ "${asg}" != "None" ]; then
        echo "ASG: ${asg}"
        aws autoscaling describe-auto-scaling-groups --region "${REGION}" \
          --auto-scaling-group-names "${asg}" \
          --query 'AutoScalingGroups[0].{Desired:DesiredCapacity,Min:MinSize,Max:MaxSize,Suspended:SuspendedProcesses[].ProcessName}' \
          --output table || true
      fi
    done
    if command -v kubectl >/dev/null; then
      echo
      kubectl get nodes -o wide 2>/dev/null || echo "(kubectl 없거나 kubeconfig 미설정)"
    fi
    echo
    echo "비용 힌트: 노드 0이어도 EKS 컨트롤 플레인 ≈ \$0.10/h (하루 ≈ \$2.4) + NAT."
    echo "완전 끄기(존 유지): ./scripts/terraform-destroy-keep-dns.sh — docs/eks-start-stop.md"
    ;;
  *)
    echo "unknown command: ${cmd}" >&2
    exit 1
    ;;
esac

#!/usr/bin/env bash
# EKS 비용 절약: 워커 노드만 끄기/켜기 (컨트롤 플레인은 유지 → 약 $0.10/h)
#
# 사용:
#   export EKS_CLUSTER_NAME=aniverse-eks
#   export EKS_NODEGROUP_NAME=aniverse-nodes   # 여러 개면 공백 구분
#   ./scripts/eks-stop.sh     # desired=0
#   ./scripts/eks-start.sh    # desired 복구 (기본 2)
#   ./scripts/eks-status.sh
#
# 완전 삭제(컨트롤 플레인 비용까지 0)는 Terraform destroy — docs/eks-start-stop.md
set -euo pipefail

REGION="${AWS_REGION:-ap-northeast-2}"
CLUSTER="${EKS_CLUSTER_NAME:-aniverse-eks}"
NODEGROUPS="${EKS_NODEGROUP_NAME:-aniverse-nodes}"
DESIRED="${EKS_DESIRED_SIZE:-2}"
MIN_START="${EKS_MIN_SIZE:-0}"
MAX_SIZE="${EKS_MAX_SIZE:-4}"

need_aws() {
  command -v aws >/dev/null || { echo "aws CLI 필요" >&2; exit 1; }
}

list_ngs() {
  # shellcheck disable=SC2086
  for ng in ${NODEGROUPS}; do
    echo "${ng}"
  done
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

cmd="$(basename "$0")"
need_aws

case "${cmd}" in
  eks-stop.sh)
    echo "Stopping workers on ${CLUSTER} (control plane stays UP ~\$0.10/h)"
    for ng in $(list_ngs); do
      scale_ng "${ng}" 0 "${MAX_SIZE}" 0
    done
    echo "OK — nodes scaling to 0. Check: ./scripts/eks-status.sh"
    ;;
  eks-start.sh)
    echo "Starting workers on ${CLUSTER} (desired=${DESIRED})"
    for ng in $(list_ngs); do
      scale_ng "${ng}" "${MIN_START}" "${MAX_SIZE}" "${DESIRED}"
    done
    echo "OK — wait 2~5m then: kubectl get nodes"
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
    done
    if command -v kubectl >/dev/null; then
      echo
      kubectl get nodes -o wide 2>/dev/null || echo "(kubectl 없거나 kubeconfig 미설정)"
    fi
    echo
    echo "비용 힌트: 노드 0이어도 EKS 컨트롤 플레인 ≈ \$0.10/h (하루 ≈ \$2.4)."
    echo "완전 끄기: Terraform으로 클러스터 destroy — docs/eks-start-stop.md"
    ;;
  *)
    echo "unknown command: ${cmd}" >&2
    exit 1
    ;;
esac

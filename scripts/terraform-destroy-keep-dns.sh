#!/usr/bin/env bash
# terraform destroy 하되 Route53 존 + ACM(+검증 레코드) 은 남긴다.
# 가비아 NS / 인증서를 매번 다시 맞추지 않기 위함.
#
#   cd environments/dev && ../../scripts/terraform-destroy-keep-dns.sh
# CD: workflow destroy job 이 이 스크립트를 호출.
#
# 선행: terraform-destroy-preflight.sh
#   - 노드 EC2_LINUX Access Entry 복구 + DELETE_FAILED 노드그룹 삭제
#   - Ingress ALB/ENI/EIP 잔여물 제거 (subnet/IGW DependencyViolation 방지)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEV="${ROOT}/environments/dev"
cd "${DEV}"

command -v terraform >/dev/null || { echo "terraform 필요" >&2; exit 1; }
command -v aws >/dev/null || { echo "aws CLI 필요" >&2; exit 1; }

REGION="${AWS_REGION:-ap-northeast-2}"
CLUSTER="${EKS_CLUSTER_NAME:-aniverse-eks}"
PROJECT="${PROJECT_NAME:-aniverse}"
NODE_ROLE_NAME="${EKS_NODE_ROLE_NAME:-${PROJECT}-eks-node-role}"

echo "==> preflight (ALB / EIP / nodegroup)"
chmod +x "${ROOT}/scripts/terraform-destroy-preflight.sh"
"${ROOT}/scripts/terraform-destroy-preflight.sh"

# preflight 가 AWS 에서 노드그룹을 *완전히* 지운 뒤에만 state rm.
# DELETE_FAILED 상태에서 state rm 하면 노드 IAM 롤이 먼저 지워지고
# 클러스터는 ResourceInUseException (nodegroups attached) 로 실패한다.
ng_now="$(aws eks describe-nodegroup \
  --region "${REGION}" \
  --cluster-name "${CLUSTER}" \
  --nodegroup-name "${PROJECT}-nodes" \
  --query 'nodegroup.status' --output text 2>/dev/null || echo MISSING)"
if [ "${ng_now}" = "MISSING" ] || [ "${ng_now}" = "None" ]; then
  if terraform state list 2>/dev/null | grep -q 'module.eks.aws_eks_node_group.default'; then
    echo "==> state rm module.eks.aws_eks_node_group.default (aws gone)"
    terraform state rm 'module.eks.aws_eks_node_group.default' || true
  fi
elif [ "${ng_now}" = "DELETE_FAILED" ]; then
  echo "ERROR: nodegroup still DELETE_FAILED after preflight — refusing state rm" >&2
  exit 1
fi

# 기존 클러스터에 EKS 가 자동 만든 노드 Access Entry 가 있으면 state 로 끌어와
# 노드그룹 → Access Entry 순으로 지우게 한다 (modules/eks aws_eks_access_entry.nodes).
account="$(aws sts get-caller-identity --query Account --output text)"
node_role_arn="arn:aws:iam::${account}:role/${NODE_ROLE_NAME}"
if aws eks describe-access-entry \
  --region "${REGION}" \
  --cluster-name "${CLUSTER}" \
  --principal-arn "${node_role_arn}" >/dev/null 2>&1; then
  echo "==> import module.eks.aws_eks_access_entry.nodes (if missing from state)"
  terraform import -input=false \
    'module.eks.aws_eks_access_entry.nodes' \
    "${CLUSTER}:${node_role_arn}" 2>/dev/null \
    || echo "    import skipped (already in state or unavailable)"
fi

echo "==> state list (excluding durable DNS)"
# 보존: 호스팅 영역, ACM 인증서, ACM DNS 검증 레코드
# 삭제: EKS ALB alias(apex/www) 포함 나머지 — 재apply 때 ALB 조회 후 다시 붙음
mapfile -t KEEP_HINTS < <(terraform state list 2>/dev/null | grep -E \
  'module\.dns\.aws_route53_zone\.|module\.dns\.aws_acm_certificate\.|module\.dns\.aws_route53_record\.cert_validation' \
  || true)

mapfile -t DESTROY_LIST < <(terraform state list 2>/dev/null | grep -v -E \
  'module\.dns\.aws_route53_zone\.|module\.dns\.aws_acm_certificate\.|module\.dns\.aws_route53_record\.cert_validation' \
  || true)

if [ "${#KEEP_HINTS[@]}" -gt 0 ]; then
  echo "KEEP:"
  printf '  %s\n' "${KEEP_HINTS[@]}"
fi

if [ "${#DESTROY_LIST[@]}" -eq 0 ]; then
  echo "Nothing to destroy (only durable DNS left, or empty state)."
  exit 0
fi

TARGETS=()
for r in "${DESTROY_LIST[@]}"; do
  TARGETS+=("-target=${r}")
done

echo "DESTROY ${#DESTROY_LIST[@]} resources (zone/ACM kept)..."

LOCK_TIMEOUT="${TF_LOCK_TIMEOUT:-20m}"

# 취소된 Actions run 이 S3 lockfile 을 남기면 다음 destroy 가 PreconditionFailed.
# runner@ 가 잡은 지 N분 지난 락은 force-unlock 후 재시도.
maybe_clear_stale_lock() {
  local log_file="$1"
  local lock_id who created
  # 컬러/박스 문자 무시하고 Lock Info 파싱
  lock_id="$(grep -Eo 'ID:[[:space:]]*[0-9a-f-]{36}' "${log_file}" 2>/dev/null | head -1 | awk '{print $2}' || true)"
  who="$(grep -E 'Who:[[:space:]]*' "${log_file}" 2>/dev/null | head -1 | sed -E 's/.*Who:[[:space:]]*//' | tr -d '\r' | sed 's/[[:space:]]*$//' || true)"
  created="$(grep -E 'Created:[[:space:]]*' "${log_file}" 2>/dev/null | head -1 | sed -E 's/.*Created:[[:space:]]*//' | tr -d '\r' || true)"
  if [ -z "${lock_id}" ]; then
    return 1
  fi
  echo "==> state lock held id=${lock_id} who=${who} created=${created}"
  if [[ "${who}" == runner@* ]] || [[ "${TF_FORCE_UNLOCK:-}" == "1" ]]; then
    echo "==> force-unlock stale Actions lock ${lock_id}"
    terraform force-unlock -force "${lock_id}" || true
    return 0
  fi
  echo "Refusing force-unlock for non-runner lock (set TF_FORCE_UNLOCK=1 to override)" >&2
  return 1
}

run_destroy() {
  local log
  log="$(mktemp)"
  set +e
  # shellcheck disable=SC2086
  terraform destroy -auto-approve -input=false -lock-timeout="${LOCK_TIMEOUT}" "${TARGETS[@]}" 2>&1 | tee "${log}"
  local rc=${PIPESTATUS[0]}
  set -e
  if [ "${rc}" -ne 0 ] && grep -q 'Error acquiring the state lock' "${log}"; then
    if maybe_clear_stale_lock "${log}"; then
      echo "==> retry destroy after force-unlock"
      set +e
      terraform destroy -auto-approve -input=false -lock-timeout="${LOCK_TIMEOUT}" "${TARGETS[@]}"
      rc=$?
      set -e
    fi
  fi
  rm -f "${log}"
  return "${rc}"
}

# 부분 실패 시 한 번 더: preflight 잔여 ENI 정리 후 재시도
set +e
run_destroy
rc=$?
set -e
if [ "${rc}" -ne 0 ]; then
  echo "==> destroy failed (rc=${rc}) — re-run preflight (long ENI wait) + retry once"
  # EKS ENI 해제는 첫 destroy 이후에야 보이므로 재시도에서 더 오래 대기
  DESTROY_ENI_WAIT_SEC="${DESTROY_ENI_WAIT_SEC:-900}" \
    "${ROOT}/scripts/terraform-destroy-preflight.sh"
  mapfile -t DESTROY_LIST < <(terraform state list 2>/dev/null | grep -v -E \
    'module\.dns\.aws_route53_zone\.|module\.dns\.aws_acm_certificate\.|module\.dns\.aws_route53_record\.cert_validation' \
    || true)
  if [ "${#DESTROY_LIST[@]}" -eq 0 ]; then
    echo "Nothing left to destroy after preflight."
    exit 0
  fi
  TARGETS=()
  for r in "${DESTROY_LIST[@]}"; do
    TARGETS+=("-target=${r}")
  done
  run_destroy
fi

echo
echo "OK — Route53 zone + ACM preserved."
echo "다음 기동:"
echo "  1) terraform apply  (CD면 restore-s3-assets 가 media/static 재업로드)"
echo "  2) helm upgrade -f values-eks.yaml"
echo "  3) ./scripts/terraform-rebind-eks-dns.sh"
echo "  4) DB SQL 복구 + (필요 시) ./scripts/restore-s3-assets.sh"
echo "또는 평소 비용절감: ./scripts/eks-stop.sh / eks-start.sh"

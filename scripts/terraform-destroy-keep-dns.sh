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

# preflight 가 AWS 에서 노드그룹을 지웠으면 state 만 남은 경우 제거 (TF wait DELETE_FAILED 방지)
if ! aws eks describe-nodegroup \
  --region "${REGION}" \
  --cluster-name "${CLUSTER}" \
  --nodegroup-name "${PROJECT}-nodes" >/dev/null 2>&1; then
  if terraform state list 2>/dev/null | grep -q 'module.eks.aws_eks_node_group.default'; then
    echo "==> state rm module.eks.aws_eks_node_group.default (already gone in AWS)"
    terraform state rm 'module.eks.aws_eks_node_group.default' || true
  fi
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
# 부분 실패 시 한 번 더: preflight 잔여 ENI 정리 후 재시도
set +e
terraform destroy -auto-approve -input=false "${TARGETS[@]}"
rc=$?
set -e
if [ "${rc}" -ne 0 ]; then
  echo "==> destroy failed (rc=${rc}) — re-run preflight + retry once"
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
  terraform destroy -auto-approve -input=false "${TARGETS[@]}"
fi

echo
echo "OK — Route53 zone + ACM preserved."
echo "다음 기동:"
echo "  1) terraform apply  (CD면 restore-s3-assets 가 media/static 재업로드)"
echo "  2) helm upgrade -f values-eks.yaml"
echo "  3) ./scripts/terraform-rebind-eks-dns.sh"
echo "  4) DB SQL 복구 + (필요 시) ./scripts/restore-s3-assets.sh"
echo "또는 평소 비용절감: ./scripts/eks-stop.sh / eks-start.sh"

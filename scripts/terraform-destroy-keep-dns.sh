#!/usr/bin/env bash
# terraform destroy 하되 Route53 존 + ACM(+검증 레코드) 은 남긴다.
# 가비아 NS / 인증서를 매번 다시 맞추지 않기 위함.
#
#   cd environments/dev && ../../scripts/terraform-destroy-keep-dns.sh
# CD: workflow destroy job 이 이 스크립트를 호출.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEV="${ROOT}/environments/dev"
cd "${DEV}"

command -v terraform >/dev/null || { echo "terraform 필요" >&2; exit 1; }

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
# shellcheck disable=SC2086
terraform destroy -auto-approve -input=false "${TARGETS[@]}"

echo
echo "OK — Route53 zone + ACM preserved."
echo "다음 기동:"
echo "  1) terraform apply  (CD면 restore-s3-assets 가 media/static 재업로드)"
echo "  2) helm upgrade -f values-eks.yaml"
echo "  3) ./scripts/terraform-rebind-eks-dns.sh"
echo "  4) DB SQL 복구 + (필요 시) ./scripts/restore-s3-assets.sh"
echo "또는 평소 비용절감: ./scripts/eks-stop.sh / eks-start.sh"

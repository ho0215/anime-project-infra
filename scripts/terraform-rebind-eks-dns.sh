#!/usr/bin/env bash
# EKS/Ingress 올린 뒤 Route53 alias 만 다시 맞춤 (ALB DNS 자동 조회).
#
#   ./scripts/terraform-rebind-eks-dns.sh
#
# Ingress ALB 가 아직 없으면 최대 ~5분 재시도.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}/environments/dev"

command -v terraform >/dev/null || { echo "terraform 필요" >&2; exit 1; }

STACK="${EKS_INGRESS_STACK:-aniverse/aniverse-web}"
REGION="${AWS_REGION:-ap-northeast-2}"
RETRIES="${REBIND_RETRIES:-30}"
SLEEP_SEC="${REBIND_SLEEP_SEC:-10}"

wait_for_alb() {
  command -v aws >/dev/null || return 0
  local i arns
  for ((i = 1; i <= RETRIES; i++)); do
    arns="$(aws elbv2 describe-load-balancers --region "${REGION}" \
      --query "LoadBalancers[?contains(LoadBalancerName, 'k8s-')].LoadBalancerArn" \
      --output text 2>/dev/null || true)"
    # Prefer tag-filtered lookup when possible
    if aws resourcegroupstaggingapi get-resources \
      --region "${REGION}" \
      --tag-filters "Key=ingress.k8s.aws/stack,Values=${STACK}" \
      --resource-type-filters elasticloadbalancing:loadbalancer \
      --query 'ResourceTagMappingList[0].ResourceARN' \
      --output text 2>/dev/null | grep -q 'arn:aws:elasticloadbalancing'; then
      echo "ALB found for stack=${STACK}"
      return 0
    fi
    echo "waiting for Ingress ALB (${i}/${RETRIES}) stack=${STACK}..."
    sleep "${SLEEP_SEC}"
  done
  echo "WARN: ALB not found yet — terraform apply 가 폴백/빈 alias 일 수 있음" >&2
  return 0
}

wait_for_alb

echo "==> terraform apply -target=module.dns"
terraform apply -auto-approve -input=false -target=module.dns

echo
python3 - <<'PY'
import json, subprocess
try:
    o = json.loads(subprocess.check_output(["terraform", "output", "-json"], text=True))
except Exception:
    raise SystemExit(0)
for k in ("route53_name_servers", "eks_alb_dns_resolved", "eks_ingress_hostname", "certificate_arn", "route53_zone_id"):
    if k in o:
        print(f"{k} = {o[k].get('value')}")
PY

echo "OK — dig aniverse.my / curl -sI http://aniverse.my/health/"

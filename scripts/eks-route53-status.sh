#!/usr/bin/env bash
# Route53 복구 후 할 일 요약 (Terraform apply 완료 가정)
#
#   ./scripts/eks-route53-status.sh
set -euo pipefail

REGION="${AWS_REGION:-ap-northeast-2}"
DOMAIN="${1:-aniverse.my}"

echo "==> Route53 zones matching ${DOMAIN}"
aws route53 list-hosted-zones-by-name --dns-name "${DOMAIN}." \
  --query "HostedZones[?Name=='${DOMAIN}.'].[Id,Name,ResourceRecordSetCount]" \
  --output table || true

echo
echo "==> terraform outputs (run from environments/dev if local)"
echo "    terraform output route53_name_servers"
echo "    terraform output route53_zone_id"
echo "    terraform output certificate_arn"
echo "    terraform output eks_ingress_hostname"
echo
echo "가비아: 도메인 관리 → 네임서버 → 위 output NS 4개로 교체"
echo "전파 확인: dig NS ${DOMAIN} +short"
echo "A 확인:    dig ${DOMAIN} +short"
echo "헬스:      curl -sI http://${DOMAIN}/health/"

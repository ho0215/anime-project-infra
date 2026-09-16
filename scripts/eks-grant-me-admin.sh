#!/usr/bin/env bash
# 현재 AWS 자격 증명(IAM user/role)을 aniverse-eks cluster-admin 으로 등록.
# kubectl "server has asked for the client to provide credentials" 일 때 사용.
#
#   ./scripts/eks-grant-me-admin.sh
#   kubectl get nodes
set -euo pipefail

REGION="${AWS_REGION:-ap-northeast-2}"
CLUSTER="${EKS_CLUSTER_NAME:-aniverse-eks}"

command -v aws >/dev/null || { echo "aws CLI 필요" >&2; exit 1; }

PRINCIPAL="$(aws sts get-caller-identity --query Arn --output text)"
echo "caller: ${PRINCIPAL}"

# assumed-role 세션 ARN → IAM role ARN (Access Entry 는 role/user ARN 만 받음)
if [[ "${PRINCIPAL}" == *":assumed-role/"* ]]; then
  ACCOUNT="$(echo "${PRINCIPAL}" | cut -d: -f5)"
  ROLE="$(echo "${PRINCIPAL}" | cut -d/ -f2)"
  PRINCIPAL="arn:aws:iam::${ACCOUNT}:role/${ROLE}"
  echo "role:   ${PRINCIPAL}"
fi

echo "==> create-access-entry ${CLUSTER}"
aws eks create-access-entry \
  --region "${REGION}" \
  --cluster-name "${CLUSTER}" \
  --principal-arn "${PRINCIPAL}" \
  2>/dev/null || echo "(access entry already exists — ok)"

echo "==> associate AmazonEKSClusterAdminPolicy"
aws eks associate-access-policy \
  --region "${REGION}" \
  --cluster-name "${CLUSTER}" \
  --principal-arn "${PRINCIPAL}" \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \
  --access-scope type=cluster \
  2>/dev/null || echo "(policy already associated — ok)"

aws eks update-kubeconfig --region "${REGION}" --name "${CLUSTER}" >/dev/null
echo
echo "OK — try:"
echo "  kubectl get nodes"
echo "  kubectl get sc"

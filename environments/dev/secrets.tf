# App 시크릿(DJANGO_SECRET_KEY/DB_PASSWORD/DB_ROOT_PASSWORD)의 유일한 진짜 저장소.
# Terraform은 메타데이터만 관리 — 값(secret_string)은 여기서 절대 세팅하지 않는다.
# (실제 DB 비밀번호가 tfstate에 평문으로 남는 걸 피하기 위함)
#
# 값 주입은 docs/external-secrets.md 절차대로 1회 수동으로:
#   kubectl -n aniverse get secret aniverse-app-secrets -o json | jq '.data | map_values(@base64d)' \
#     | aws secretsmanager put-secret-value --secret-id aniverse/app-secrets --secret-string file:///dev/stdin
resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "aniverse/app-secrets"
  description = "Django/DB secrets — EKS로는 External Secrets Operator가 동기화. 값은 Terraform이 아니라 수동 1회 주입(docs/external-secrets.md)."
}

# Aniverse Infrastructure (Terraform)

GitHub Secrets/Variables만 등록하면 GitHub Actions로 **인프라 Apply/Destroy → 앱 CodeDeploy**까지 자동화합니다.

## 구조

```
bootstrap/           # 최초 1회: tfstate S3 + lock + GitHub OIDC role
environments/dev/    # 루트 모듈
modules/
  network, security, nat, endpoints, database, storage,
  acm, alb, waf, redis, secrets, compute, cicd, monitoring
scripts/
  ssm-connect.sh / wait-for-ssm.sh
.github/workflows/
  terraform-ci.yml   # PR: fmt(필수) / validate / plan
  terraform-cd.yml   # main push + workflow_dispatch: apply|destroy
```

## 사전 준비 (1회)

```bash
cd bootstrap
terraform init && terraform apply
```

Outputs의 `github_actions_role_arn` 을 GitHub Actions **Variable** `AWS_ROLE_ARN` 에 등록하면
워크플로가 OIDC로 인증합니다. (미설정 시 Access Key fallback)

## GitHub Secrets / Variables

### Secrets (필수)

| Name | 설명 |
|------|------|
| `TF_VAR_DB_PASSWORD` | RDS master password |
| `TF_VAR_DJANGO_SECRET_KEY` | Django SECRET_KEY |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | OIDC 미사용 시에만 필요 |

### Secrets (선택)

| Name | 설명 |
|------|------|
| `TF_VAR_DB_SNAPSHOT_IDENTIFIER` | destroy 후 재apply 복원 스냅샷 ID |
| `TF_VAR_GEMINI_API_KEY` | Gemini 챗봇 |

### Variables

| Name | 설명 |
|------|------|
| `AWS_ROLE_ARN` | bootstrap output `github_actions_role_arn` (OIDC) |
| `ALERT_EMAIL` | CloudWatch SNS 구독 이메일 |
| `TF_VAR_RESTORE_FROM_LATEST_SNAPSHOT` | `true`/`false` |

## RDS 스냅샷 복원

CD가 **소스 파일을 패치하지 않습니다.** `TF_VAR_db_snapshot_identifier` /
`TF_VAR_restore_from_latest_snapshot` 변수로만 전달합니다.

1. Destroy → Job Summary에 최신 manual 스냅샷 ID 출력
2. Secret에 ID를 넣거나 workflow_dispatch에서 `restore_from_latest_snapshot=true`
3. Apply

## HTTPS / WAF / Secrets / Redis

- 도메인 `aniverse.my` (Route 53 호스팅 영역 기존) + ACM + ALB 443
- WAFv2 (Common / KnownBadInputs / SQLi / rate limit) → ALB
- ALB access logs → S3
- Secrets Manager → EC2 user_data가 `.env` 생성 (LT에 평문 시크릿 없음)
- ElastiCache Redis → Django Channels (`REDIS_URL`)

## 앱 저장소 연동

| anime-project | Terraform output |
|---------------|------------------|
| `S3_BUCKET_NAME` | `deploy_bucket_name` |
| 접속 URL | `app_url` (`https://aniverse.my`) |

## 로컬 실행

```bash
cd environments/dev
export TF_VAR_db_password='...'
export TF_VAR_django_secret_key='...'
terraform init && terraform apply
```

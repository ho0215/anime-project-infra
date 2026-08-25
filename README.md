# Aniverse Infrastructure (Terraform)

GitHub Secrets에 자격 증명만 등록하면 GitHub Actions로 **인프라 Apply/Destroy → 앱 CodeDeploy**까지 자동화하는 구성을 목표로 합니다.

## 구조

```
bootstrap/           # 최초 1회: tfstate S3 + lock 테이블
environments/dev/    # 루트 모듈 (network→security→nat→database→storage→compute→cicd→monitoring)
modules/
  network, security, nat, database, storage, compute, cicd, monitoring
.github/workflows/
  terraform-ci.yml   # PR: fmt / validate / plan
  terraform-cd.yml   # main push: apply / workflow_dispatch: apply|destroy
```

## 사전 준비 (1회)

```bash
cd bootstrap
terraform init && terraform apply
```

이후 `environments/dev` 는 S3 백엔드(`aniverse-tfstate`)를 사용합니다.

## GitHub Secrets / Variables

### Repository Secrets (필수)

| Name | 설명 |
|------|------|
| `AWS_ACCESS_KEY_ID` | Terraform/배포용 IAM 사용자 액세스 키 |
| `AWS_SECRET_ACCESS_KEY` | 시크릿 키 |
| `TF_VAR_DB_PASSWORD` | RDS master password (`TF_VAR_db_password`로 주입) |
| `TF_VAR_DJANGO_SECRET_KEY` | Django `SECRET_KEY` |

### Repository Secrets (선택)

| Name | 설명 |
|------|------|
| `TF_VAR_DB_SNAPSHOT_IDENTIFIER` | destroy 후 재apply 시 복원할 스냅샷 ID |

### Repository Variables (선택)

| Name | 설명 |
|------|------|
| `ALERT_EMAIL` | CloudWatch 알람 SNS 구독 이메일 (비우면 monitoring 미생성) |
| `TF_VAR_RESTORE_FROM_LATEST_SNAPSHOT` | `true`/`false` — 최신 manual 스냅샷 자동 복원 |

### IAM 권한 (최소 가이드)

해당 IAM 사용자/롤에 VPC, EC2, ELB, ASG, RDS, S3, EFS, IAM(PassRole 포함), CodeDeploy, CloudWatch, SNS 권한이 필요합니다. 학습용으로는 `AdministratorAccess`로 시작해도 됩니다.

## RDS 영속성 (destroy → apply)

1. RDS는 `skip_final_snapshot = false` 로 **최종 스냅샷을 남기고** 삭제됩니다.
2. 자동 백업 보관: 7일 (`backup_retention_period`).
3. Destroy 워크플로가 최신 manual 스냅샷 ID를 Job Summary에 출력합니다.
4. 다시 Apply 할 때:
   - Secret `TF_VAR_DB_SNAPSHOT_IDENTIFIER`에 스냅샷 ID를 넣거나
   - `workflow_dispatch` Apply에서 `restore_from_latest_snapshot=true`
5. 최초 배포(스냅샷 없음)에서는 복원 플래그를 **끄세요**. 스냅샷이 없으면 plan/apply가 실패합니다.

## 앱 저장소 연동

Apply 성공 후 Output을 **anime-project** 저장소에 등록:

| anime-project Secret/Var | Terraform output |
|--------------------------|------------------|
| `S3_BUCKET_NAME` | `deploy_bucket_name` |
| (하드코딩 기본값) CodeDeploy app/group | `aniverse-app` / `aniverse-deployment-group` |

## 로컬 실행 예

```bash
cd environments/dev
export TF_VAR_db_password='...'
export TF_VAR_django_secret_key='...'
terraform init
terraform plan
terraform apply
```

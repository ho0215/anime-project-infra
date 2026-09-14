# Infra Terraform — GitHub OIDC 켜기

앱 ECR OIDC와 **별도**입니다. 이 문서는 `anime-project-infra` Terraform CI/CD용입니다.

> `terraform apply`(environments/dev) 를 돌리는 게 아닙니다.  
> Variable만 켜고, 먼저 **OIDC smoke** 워크플로로 AssumeRole만 확인하세요.

## 역할 (이미 bootstrap에 있음)

| 항목 | 값 |
|------|-----|
| Role | `aniverse-github-actions-terraform` |
| ARN | `arn:aws:iam::679583587966:role/aniverse-github-actions-terraform` |
| trust | `repo:ho0215/anime-project-infra:*` (+ immutable ID 형식) |
| 권한 | `AdministratorAccess` (학습용 — 나중에 축소 가능) |

## 1) GitHub Variables (`anime-project-infra`)

Settings → Secrets and variables → Actions → **Variables**

| Name | Value |
|------|--------|
| `AWS_ROLE_ARN` | `arn:aws:iam::679583587966:role/aniverse-github-actions-terraform` |
| `AWS_USE_OIDC` | `true` |

앱 레포(`anime-project`) Variable과 **이름이 같아도 레포마다 값이 다릅니다.**  
앱은 ECR 역할, infra는 Terraform 역할을 넣습니다.

## 2) 스모크 테스트 (인프라 변경 없음)

Actions → **OIDC smoke (infra)** → Run workflow

성공 시 Summary에:

- OIDC claims (`sub` 등)
- `assumed: arn:aws:sts::679583587966:assumed-role/aniverse-github-actions-terraform/...`

실패 시 `Not authorized to perform sts:AssumeRoleWithWebIdentity` → claims의 `sub`와 IAM trust 비교.

## 3) 실제 CD에 적용

스모크 통과 후:

- `Terraform CD (Apply / Destroy)` / `Terraform CI (Plan on PR)` 가  
  `AWS_USE_OIDC=true` 이면 **자동으로 OIDC** 사용 (코드 이미 반영됨)
- job에 GitHub **Environment** 를 다시 붙이지 말 것 (예전에 sub 불일치 원인)

## 예전에 안 됐던 이유 (요약)

1. CD에 `environment: production` → `sub`가 `...:environment:production`
2. trust를 `repository` 클레임만으로 바꿈 → AWS가 거절 (`sub` 필수)
3. apply가 급해서 Access Key로 우회 (`AWS_USE_OIDC` 기본 off)

지금은 environment 제거 + scoped `sub` + 앱에서 동일 패턴 검증 완료.

## 끄기

Variable `AWS_USE_OIDC`를 지우거나 `false` → Access Key fallback.

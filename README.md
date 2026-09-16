# Aniverse Infrastructure (Terraform) — EKS only

GitHub Actions로 **VPC · EKS · ECR · Route53/ACM · S3** apply/destroy를 자동화합니다.  
앱 배포는 anime-project의 **Helm + ECR** 경로를 씁니다.

## 구조

```
bootstrap/           # 최초 1회: tfstate S3 + lock + GitHub OIDC role
environments/dev/    # 루트 모듈
modules/
  network, security, nat, storage(S3), dns, ecr, eks
scripts/
  eks-start.sh / eks-stop.sh / eks-status.sh
  terraform-destroy-keep-dns.sh
  terraform-rebind-eks-dns.sh
  eks-grant-me-admin.sh / eks-route53-status.sh
.github/workflows/
  terraform-ci.yml   # PR: fmt / validate / plan
  terraform-cd.yml   # apply | destroy(keep-dns)
  eks-start-stop.yml
```

비용: [docs/eks-start-stop.md](./docs/eks-start-stop.md) · 구성도: [docs/aniverse-eks-architecture-as-is.png](./docs/aniverse-eks-architecture-as-is.png)

## 사전 준비 (1회)

```bash
cd bootstrap
terraform init && terraform apply
```

- `github_actions_role_arn` → infra Variable `AWS_ROLE_ARN`
- `github_actions_app_ecr_role_arn` → anime-project Variable `AWS_ROLE_ARN`
- 각 레포 `AWS_USE_OIDC=true` (아니면 Access Key fallback)

## GitHub Secrets / Variables

| Name | 필수 | 설명 |
|------|------|------|
| `AWS_ROLE_ARN` | OIDC 시 | bootstrap infra role |
| `AWS_USE_OIDC` | 권장 | `true` |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | OIDC 미사용 시 | — |

DB/Django 시크릿은 **Helm Secret** 으로 앱 레포에서 관리합니다 (Terraform 불필요).

## 로컬

```bash
cd environments/dev
terraform init && terraform apply
terraform output route53_name_servers
terraform output eks_kubeconfig_hint
```

앱 쪽: `helm upgrade … -f values-eks.yaml` → `./scripts/eks-bind-domain.sh`

## destroy

CD `action=destroy` 또는 `./scripts/terraform-destroy-keep-dns.sh`  
→ Route53 존 + ACM 유지 (가비아 NS 고정).

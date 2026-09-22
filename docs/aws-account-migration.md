# AWS 계정 이관 가이드 (Aniverse EKS)

옛 계정(`679583587966`)에서 **새 AWS 계정**으로 Aniverse 인프라·앱·DNS·CI를 옮길 때 쓰는 체크리스트다.  
대상 스택: **EKS + Helm/Argo + ECR + S3 + Route53/ACM + GitHub OIDC** (EC2/CodeDeploy 경로 제외).

> 작성 기준: `anime-project` / `anime-project-infra` `main` (2026-09 시점)  
> 도메인: `aniverse.my` · 리전: `ap-northeast-2`

---

## 0. 한눈에 보기

| 단계 | 내용 | 예상 산출물 |
|------|------|-------------|
| A | 새 계정·결제·MFA | 계정 ID |
| B | bootstrap (tfstate S3 + OIDC 역할) | `AWS_ROLE_ARN` 2개 |
| C | GitHub Variables 교체 | OIDC smoke 성공 |
| D | Terraform apply (EKS 스택) | 클러스터·ECR·S3·ACM ARN |
| E | Helm values / 앱 하드코딩 교체 | 새 ECR·IRSA·버킷·인증서 |
| F | DNS (가비아 NS → 새 Route53) | HTTPS 동작 |
| G | 데이터 (DB SQL + media/S3) | 사이트 컨텐츠 복구 |
| H | Argo/Actions 검증 | GitOps 배포 1회 |
| I | 옛 계정 정리 | 과금·키 정리 |

**원칙**

- 장기 Access Key는 **쓰지 않는다** (유출로 Block 난 경위).
- CI는 **OIDC만** (`AWS_USE_OIDC=true`).
- Secret(Django/DB)은 **git에 넣지 않는다** (Argo live Secret / helm parameters).

---

## 1. 계정에 묶인 값 (반드시 갈아끼울 것)

### 1.1 옛 계정에서 쓰던 값

| 구분 | 옛 값 (예시) |
|------|----------------|
| Account ID | `679583587966` |
| Terraform state 버킷 | `aniverse-tfstate-ho0215` |
| Infra OIDC role | `arn:aws:iam::679583587966:role/aniverse-github-actions-terraform` |
| App ECR OIDC role | bootstrap output `github_actions_app_ecr_role_arn` |
| ECR 이미지 | `679583587966.dkr.ecr.ap-northeast-2.amazonaws.com/aniverse` |
| Static 버킷 | `aniverse-static-679583587966-ap-northeast-2` |
| Web IRSA | `arn:aws:iam::679583587966:role/aniverse-web-s3-irsa` |
| ACM | `arn:aws:acm:ap-northeast-2:679583587966:certificate/e217dacc-...` |

### 1.2 파일별 수정 위치

**`anime-project-infra`**

| 파일 | 바꿀 것 |
|------|---------|
| `bootstrap/main.tf` | state 버킷 이름 (전역 유일해야 함) |
| `environments/dev/backend.tf` | `bucket = "aniverse-tfstate-..."` → 새 버킷 |
| `bootstrap/github_oidc.tf` | org/repo는 그대로여도 됨 (역할은 새 계정에 생성) |
| `docs/infra-oidc.md` | ARN·Account ID 문서 갱신 |
| `environments/dev/terraform.tfvars` (로컬, 커밋 금지) | `eks_cluster_admin_arns` 에 **새 계정 IAM ARN** |

**`anime-project`**

| 파일 | 바꿀 것 |
|------|---------|
| `deploy/helm/aniverse/values-eks.yaml` | `image.repository`, IRSA `role-arn`, `AWS_STORAGE_BUCKET_NAME`, `certificate-arn` |
| (필요 시) `scripts/eks-bind-domain.sh` / `argocd-eks-install.sh` | 기본 계정·클러스터명이 하드코딩돼 있으면 |
| `.github/workflows/docker-build.yml` | 보통 변수/OIDC로 동작 — **레포 Variable**의 ECR 역할만 새 ARN |

**GitHub (콘솔)**

| 레포 | Variable / Secret |
|------|-------------------|
| `anime-project-infra` | `AWS_ROLE_ARN` = **Terraform용** OIDC role · `AWS_USE_OIDC=true` |
| `anime-project` | `AWS_ROLE_ARN` = **ECR push용** OIDC role · `AWS_USE_OIDC=true` |
| 양쪽 | 옛 `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` **삭제** |
| `anime-project` | Helm용 시크릿은 Argo/클러스터 Secret으로 (레포 Secret에 Django 키를 두던 방식이면 재등록) |

---

## 2. 단계별 절차

### A. 새 AWS 계정 준비

1. 새 계정 생성 · 루트 MFA · 결제 수단 · AWS Budgets(한도 알람).
2. 본인용 IAM 사용자/역할 (콘솔·kubectl용). **AdministratorAccess는 학습 초기에만**, 이후 축소.
3. 계정 ID 메모: `NEW_ACCOUNT_ID=xxxxxxxxxxxx`

### B. Bootstrap (새 계정에서 1회)

```bash
# 새 계정 자격으로
cd anime-project-infra/bootstrap

# 1) state 버킷 이름을 새 계정 전용으로 변경 (예: aniverse-tfstate-<이름>-<account>)
#    bootstrap/main.tf 의 bucket 이름 수정

terraform init
terraform apply
terraform output
```

받을 값:

| Output | 용도 |
|--------|------|
| state 버킷 이름 | `environments/dev/backend.tf` |
| `github_actions_role_arn` | infra 레포 `AWS_ROLE_ARN` |
| `github_actions_app_ecr_role_arn` | app 레포 `AWS_ROLE_ARN` |

그다음:

```bash
# environments/dev/backend.tf 의 bucket 을 새 state 버킷으로 수정 후
cd ../environments/dev
terraform init -reconfigure
```

> 옛 state를 새 계정으로 **복사하지 않는다**. 새 계정은 **빈 state에서 apply**가 맞다.  
> (리소스 ID·ARN이 전부 달라짐)

### C. GitHub OIDC 연결

1. infra Settings → Variables  
   - `AWS_ROLE_ARN` = bootstrap Terraform role  
   - `AWS_USE_OIDC` = `true`
2. app Settings → Variables  
   - `AWS_ROLE_ARN` = bootstrap ECR role  
   - `AWS_USE_OIDC` = `true`
3. Actions → **OIDC smoke (infra)** 실행 → AssumeRole 성공 확인  
4. (앱) docker-build가 OIDC로 ECR 로그인하는지 스모크

참고: `docs/infra-oidc.md`  
주의: CD job에 GitHub **Environment**를 붙이면 `sub`가 바뀌어 trust와 충돌할 수 있음 → **Environment 미사용**.

### D. Terraform apply (EKS 스택)

```bash
cd environments/dev
# terraform.tfvars 예:
#   eks_cluster_admin_arns = ["arn:aws:iam::NEW_ACCOUNT_ID:user/너"]
terraform plan
terraform apply
```

또는 GitHub Actions **Terraform CD → apply** (OIDC).

확인용 output (이름은 레포에 따라 약간 다를 수 있음):

```bash
terraform output
# 특히:
# - eks_cluster_name / kubeconfig hint
# - ecr_repository_url
# - static_bucket_name
# - certificate_arn / app_url
# - app_s3_irsa_role_arn
# - route53_name_servers
```

**적용되는 모듈(대략):** `network`, `nat`, `security`, `storage(S3)`, `dns(Route53+ACM)`, `ecr`, `eks`(ALB Controller, EBS CSI, CA, IRSA 등)

### E. 앱 Helm values 갱신

`anime-project/deploy/helm/aniverse/values-eks.yaml` 예시 변경:

```yaml
image:
  repository: <NEW_ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/aniverse
  # tag 는 CI bump 또는 첫 배포 후 자동

serviceAccount:
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::<NEW_ACCOUNT_ID>:role/aniverse-web-s3-irsa"

config:
  AWS_STORAGE_BUCKET_NAME: "aniverse-static-<NEW_ACCOUNT_ID>-ap-northeast-2"
  # 도메인은 그대로 aniverse.my 가능

ingress:
  annotations:
    alb.ingress.kubernetes.io/certificate-arn: "<terraform output certificate_arn>"
```

PR/커밋 후:

1. `docker-build`로 새 ECR에 이미지 push  
2. Argo 설치·Application sync (`scripts/argocd-eks-install.sh` / infra `argocd-eks` 워크플로)  
3. live Secret으로 `DJANGO_SECRET_KEY`, `DB_PASSWORD`, `DB_ROOT_PASSWORD` 주입

### F. DNS · HTTPS

1. `terraform output route53_name_servers` 확인  
2. **가비아(또는 도메인 등록처)** NS를 **새 계정 Route53 존** NS로 변경  
3. ACM이 `ISSUED` 될 때까지 대기 (DNS 검증 레코드는 Terraform이 존에 넣음)  
4. Ingress ALB 생성 후 alias 연결  
   - `anime-project`의 `eks-bind-domain.sh` 또는  
   - infra `scripts/terraform-rebind-eks-dns.sh`  
5. 확인: `curl -sI https://aniverse.my/health/`

> 옛 계정에 존을 “keep”해 둔 상태였다면:  
> - **A안**: 새 계정에 존을 새로 만들고 가비아 NS만 새 NS로 교체 (권장, 단순)  
> - **B안**: 존 이전(계정 간 Route53 이전) — 절차가 더 김

### G. 데이터 이관

| 데이터 | 방법 |
|--------|------|
| DB | Git의 `data/aniverse_backup.sql` → Helm `dbRestore` Job (이미 `sqlUrl`이 raw GitHub) |
| media / static | 옛 S3 접근 가능하면 `aws s3 sync` → 새 버킷. **Block/파괴면** 레포 `media/`·`static/` + `scripts/restore-s3-assets.sh` / Sync media 워크플로 |
| 시크릿 | 새로 발급·설정 (옛 키 재사용 비권장) |

### H. 검증 체크리스트

- [ ] OIDC smoke (infra) 성공  
- [ ] `terraform apply` 완료, 노드 Ready  
- [ ] ECR에 `aniverse:sha-*` 이미지 존재  
- [ ] Argo Application Healthy / Synced  
- [ ] `https://aniverse.my/health/` 200  
- [ ] 정적·미디어 S3 로딩  
- [ ] IRSA로 업로드(또는 collectstatic 경로) 동작  
- [ ] db-restore 후 주요 페이지·로그인  
- [ ] (선택) HPA 부하 테스트 — 파드만 증가

### I. 옛 계정 정리

1. Block 해제 여부와 무관하게 **유출 Access Key는 이미 삭제** 상태 유지  
2. 새 계정으로 DNS 이전 완료 후, 옛 계정 리소스 destroy (과금 방지)  
3. Support 케이스는 “계정 이전 완료, 옛 계정 제한은 참고만” 정도로 남겨도 됨  
4. GitHub에서 옛 계정 ARN Variable 잔존 여부 재확인

---

## 3. 워크플로·스크립트 대응표

| 작업 | 어디서 |
|------|--------|
| Infra plan | `anime-project-infra` → Terraform CI |
| Infra apply/destroy | Terraform CD (`destroy`는 Route53+ACM keep) |
| EKS 비용 절약 | `eks-start-stop.yml` / `scripts/eks-start.sh` `eks-stop.sh` |
| 앱 이미지 | `anime-project` → `docker-build.yml` |
| Argo on EKS | infra `argocd-eks.yml` + app `scripts/argocd-eks-install.sh` |
| Media → S3 | infra `sync-media-s3.yml` / `scripts/restore-s3-assets.sh` |

---

## 4. 비용·범위 메모 (멘토링과 맞춤)

- **한 계정·한 EKS**로 검증하는 것이 학습/발표에 충분하다.  
- dev/staging/prod 전부 새 계정에 복제하면 **비용만 증가**.  
- 감사로그·풀 CloudWatch는 필요 시 범위 한정.  
- NAT·노드 start/stop으로 평소 비용 절감 (`docs/eks-start-stop.md`).

---

## 5. 자주 하는 실수

| 실수 | 결과 |
|------|------|
| 옛 `values-eks.yaml` ARN 그대로 | ImagePullBackOff / IRSA 403 / HTTPS 인증서 오류 |
| state 버킷만 바꾸고 bootstrap OIDC 안 함 | Actions AssumeRole 실패 |
| Access Key를 새 계정에도 등록 | 보안 리스크 재발 |
| 가비아 NS 미변경 | ACM Pending / 도메인 옛 ALB |
| destroy 중 Cancel | S3 state lock 잔존 → `force-unlock` 필요 (`terraform-destroy-keep-dns.sh`가 runner 락 처리) |
| GitHub Environment를 CD에 연결 | OIDC `sub` 불일치 |

---

## 6. 최소 일정 예시

| Day | 할 일 |
|-----|--------|
| 1 | 새 계정 + bootstrap + GitHub Variable + OIDC smoke |
| 2 | terraform apply + values-eks 교체 PR + 첫 이미지 push |
| 3 | DNS NS 교체 + ACM + Argo sync + DB/media 복구 |
| 4 | 스모크·HPA·발표용 캡처 | 옛 계정 정리 |

---

## 7. 관련 문서

- [docs/infra-oidc.md](./infra-oidc.md) — OIDC 설정  
- [docs/eks-start-stop.md](./eks-start-stop.md) — 비용·기동  
- [docs/eks-migration-plan.md](./eks-migration-plan.md) — Phase A~D  
- [docs/troubleshooting-log.md](./troubleshooting-log.md) — Block·destroy 이슈  
- 앱: `deploy/helm/aniverse/values-eks.yaml`, `docs/argocd-lab.md`

---

## 8. 이관 완료 정의

다음이 모두 새 계정에서 되면 이관 완료로 본다.

1. `https://aniverse.my` 가 **새 계정 ALB/ACM**으로 응답  
2. GitHub Actions가 **새 계정 OIDC 역할**만 사용  
3. Argo가 **새 ECR 이미지 태그**를 sync  
4. S3 media/static + DB 데이터가 서비스에 보임  
5. 문서·values에 옛 Account ID(`679583587966`) 잔존 없음 (검색으로 확인)

```bash
# 레포 루트에서 잔존 검색
rg '679583587966' -g '!docs/troubleshooting-log.md' -g '!docs/aws-account-migration.md'
```

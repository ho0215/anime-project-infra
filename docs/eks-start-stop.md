# EKS 켰다 / 끄기 (비용 절약)

EKS는 **계속 켜둘 필요 없음**. 작업할 때만 켜고, 끝나면 끄는 걸 기본으로 한다.

## 한눈에

| 명령 | 하는 일 | 남는 비용 |
|------|---------|-----------|
| `./scripts/eks-stop.sh` | 워커 **desired=0** + ASG 직접 0 + **NAT stop** (Autoscaler Launch suspend) | 컨트롤 플레인 ≈ **$0.10/h** (+ EBS) |
| `./scripts/eks-start.sh` | **NAT start** → ASG resume → 워커 복구 | 노드 + NAT + 컨트롤 |
| `./scripts/eks-status.sh` | 상태 확인 (노드그룹·ASG·NAT) | — |
| Terraform **destroy** (`terraform-destroy-keep-dns.sh`) | 인프라 삭제, **Route53 존·ACM 유지** | DNS≈0, NS 그대로 |
| Terraform **destroy 전체** (비권장) | 존까지 삭제 | 가비아 NS 다시 등록 필요 |

> **평소 비용 절감은 `eks-stop` / `eks-start`.**  
> destroy 는 가끔만. destroy 해도 **aniverse.my 호스팅 영역 NS는 안 바뀜**.

## 사전 설정 (한 번)

```bash
export AWS_REGION=ap-northeast-2
export EKS_CLUSTER_NAME=aniverse-eks          # 실제 클러스터 이름
export EKS_NODEGROUP_NAME=aniverse-nodes      # 여러 개면: "ng1 ng2"
export EKS_DESIRED_SIZE=2                     # start 시 노드 수

aws sts get-caller-identity
aws eks update-kubeconfig --region "$AWS_REGION" --name "$EKS_CLUSTER_NAME"
```

`~/.bashrc`에 export 넣어 두면 편하다.

## 매일 쓰는 법 (권장)

```bash
cd anime-project-infra

# 작업 시작 (노드 Ready 될 때까지 대기)
./scripts/eks-start.sh
kubectl get nodes

# 앱이 이미 helm 으로 올라가 있으면 바로 접속
# (Route53 alias · ALB 는 stop/start 동안 유지 → DNS 재바인딩 불필요)
curl -sI http://aniverse.my/health/

# 작업 끝
./scripts/eks-stop.sh
```

## destroy 후 다시 올릴 때

CD destroy 는 `scripts/terraform-destroy-keep-dns.sh` 를 씀 (존·ACM 보존).

S3 버킷은 `force_destroy=true` 라 **객체(사진·css·img)까지 삭제**된다.  
버킷 이름은 계정+리전으로 고정이라 URL은 그대로이고, **내용은 git에서 다시 올려야** 한다.

```bash
# 1) terraform apply  (EKS·S3 등 재생성)
#    → CD 가 apply 직후 Sync media → S3 (restore-s3-assets) 도 실행
# 2) helm upgrade --install aniverse ... -f values-eks.yaml
# 3) Route53 alias 를 새 ALB 에 재바인딩 (태그로 ALB 자동 조회)
./scripts/terraform-rebind-eks-dns.sh
# 4) DB PVC 도 날아감 → Helm dbRestore Job 이 SQL 자동 복구
#    (anime-project values-eks.yaml dbRestore.enabled, docs/db-restore.md)
# 5) (CD 실패·수동 시) S3 자산 재업로드
#    Actions → Sync media → S3  또는
#    APP_DIR=../anime-project STATIC_BUCKET_NAME=aniverse-static-... \
#      ./scripts/restore-s3-assets.sh

dig +short aniverse.my
curl -sI https://aniverse.my/health/
# 사진 샘플
curl -sI "https://aniverse-static-841535407395-ap-northeast-2.s3.ap-northeast-2.amazonaws.com/goods_images/타마마.jpeg"
```

가비아 NS 를 유지하려면 **반드시** keep-dns destroy 를 쓴다.  
존을 지우면 NS 가 바뀌어 가비아를 다시 고쳐야 한다.

### destroy → reapply 후 “사진까지” 같은지?

| 항목 | destroy 후 | 복구 |
|------|------------|------|
| Route53 존 / ACM | 유지 | 재발급 불필요 |
| S3 버킷·객체 | 삭제 | apply + **media/static sync** |
| EKS / ALB | 삭제 | apply + helm + DNS rebind |
| DB (EBS PVC) | 삭제 | Argo/Helm **dbRestore Job** (SQL) |
| ECR 이미지 | 모듈에 있으면 삭제될 수 있음 | CI 재 push |

검증용: Actions **Verify S3 wipe → restore** (버킷 비우기 시뮬레이션 → sync → HTTP 200).

## GitHub Actions으로도 가능

워크플로: **EKS start/stop** (`workflow_dispatch`)

1. Actions → **EKS start/stop** → Run workflow  
2. `action`: `start` | `stop` | `status`  
3. 인증 Variables (infra 레포): (OIDC) `AWS_ROLE_ARN` + `AWS_USE_OIDC=true`  
4. 클러스터 이름 Variables는 **선택** — 없으면 기본 `aniverse-eks` / `aniverse-nodes`  
   (다른 이름이면 `EKS_CLUSTER_NAME`, `EKS_NODEGROUP_NAME` 설정)

브라우저에서 끄기 좋다.

## 며칠 이상 안 쓸 때 (완전 끄기)

노드만 0으로 두면 **컨트롤 플레인이 계속 과금**된다.  
며칠~2주 쉴 거면 클러스터를 지우는 편이 싸다.

```bash
# CD: Terraform CD → action=destroy (keep-dns)
# 로컬:
./scripts/terraform-destroy-keep-dns.sh
```

다시 켤 때 `terraform apply` → helm → `./scripts/terraform-rebind-eks-dns.sh`.

## 안 지워도 되는 것

- **Route53 호스팅 영역** (가비아 NS 고정) — destroy 시에도 유지
- **ACM 인증서** (+ DNS 검증 레코드) — HTTPS 재기동 빠르게
- ECR 이미지
- GitHub 코드 · 매니페스트
- Terraform state / (공유 시) VPC

## 팀 약속 (추천)

1. **당일 실습만** → `eks-stop` (노드 0)  
2. **2일 이상 안 씀** → keep-dns destroy  
3. Budgets 알람 (예: $30)  
4. 클러스터/노드그룹 이름은 Variables·이 문서에 통일

# EKS 켰다 / 끄기 (비용 절약)

EKS는 **계속 켜둘 필요 없음**. 작업할 때만 켜고, 끝나면 끄는 걸 기본으로 한다.

## 한눈에

| 명령 | 하는 일 | 남는 비용 |
|------|---------|-----------|
| `./scripts/eks-stop.sh` | 워커 노드 **0대** | 컨트롤 플레인 ≈ **$0.10/h** (하루 ~$2.4) |
| `./scripts/eks-start.sh` | 워커 다시 올림 (기본 2대) | 노드 + 컨트롤 |
| `./scripts/eks-status.sh` | 상태 확인 | — |
| Terraform **destroy** (클러스터) | 완전 삭제 | **≈ $0** (ECR·코드는 유지) |

> 아직 EKS Terraform이 없으면 서이가 클러스터·노드그룹 만든 뒤  
> 아래 이름만 환경변수로 맞추면 된다.

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

## 매일 쓰는 법

```bash
cd anime-project-infra

# 작업 시작
./scripts/eks-start.sh
# 2~5분 후
kubectl get nodes

# 작업 끝 (노드만 꺼서 EC2비 절약)
./scripts/eks-stop.sh
./scripts/eks-status.sh
```

## GitHub Actions으로도 가능

워크플로: **EKS start/stop** (`workflow_dispatch`)

1. Actions → **EKS start/stop** → Run workflow  
2. `action`: `start` | `stop` | `status`  
3. Variables (infra 레포):
   - `EKS_CLUSTER_NAME`
   - `EKS_NODEGROUP_NAME`
   - (OIDC) `AWS_ROLE_ARN` + `AWS_USE_OIDC=true`

브라우저에서 끄기 좋다.

## 며칠 이상 안 쓸 때 (완전 끄기)

노드만 0으로 두면 **컨트롤 플레인이 계속 과금**된다.  
며칠~2주 쉴 거면 클러스터를 지우는 편이 싸다.

```bash
# 실제 모듈 경로는 서이 Terraform에 맞게
terraform destroy -target=module.eks
```

다시 켤 때 `terraform apply` + kubeconfig + 앱/Argo 재적용.

## 안 지워도 되는 것

- ECR 이미지
- GitHub 코드 · 매니페스트
- Terraform state / (공유 시) VPC

## 팀 약속 (추천)

1. **당일 실습만** → `eks-stop` (노드 0)  
2. **2일 이상 안 씀** → 클러스터 destroy  
3. Budgets 알람 (예: $30)  
4. 클러스터/노드그룹 이름은 Variables·이 문서에 통일

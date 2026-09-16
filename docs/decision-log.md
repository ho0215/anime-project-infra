# Aniverse 결정 로그

아키텍처·인프라·비용 관련 **팀 합의**를 날짜순으로 남긴다. (최신이 위)

관련: [아키텍처 As-Is/To-Be](./architecture-as-is-to-be.md) · [EKS 전환 계획서](./eks-migration-plan.md) · [트러블슈팅](./troubleshooting-log.md)

---

## 2026-09-16

### D-007 — Terraform EKS-only 정리

| 항목 | 내용 |
|------|------|
| 결정 | 루트 모듈에서 EC2 ASG · classic ALB · CodeDeploy · RDS · Redis · EFS · WAF · Secrets Manager · SSM endpoints · monitoring 제거 |
| 유지 | network · nat · security(NAT SG) · storage(S3) · dns · ecr · eks |
| 앱 DB | Helm MariaDB StatefulSet + EBS PVC |
| 사유 | 비용 · 운영 단순화. As-Is는 git 태그 `v1-ec2-codedeploy` 로 보존 |
| 주의 | 다음 apply 시 state에 남은 레거시 리소스는 **destroy** 됨 |

---

## 2026-09-11

### D-001 — AWS 계정 · 비용

| 항목 | 내용 |
|------|------|
| 결정 | EKS · 관련 실습 리소스는 **현우 AWS 계정**에서 진행 |
| 비용 | **엔빵** (팀 분담) |
| 사유 | 멘토링 가이드 · 크레딧/결제 창구 단일화 |
| 주의 | Budgets/알람 설정 · 미사용 EKS 클러스터 삭제 |

### D-002 — As-Is 코드 보존

| 항목 | 내용 |
|------|------|
| 결정 | EC2/ASG/CodeDeploy 안정본을 git 태그로 고정 |
| 태그 | `v1-ec2-codedeploy` (`anime-project`, `anime-project-infra`) |
| 사유 | 포트폴리오 비교 · EKS 작업 중 롤백/참조 |

### D-003 — DB To-Be (초안 · 멘토링)

| 항목 | 내용 |
|------|------|
| 결정 | To-Be DB는 **Pod(StatefulSet) + EBS PVC** 우선 (RDS 상시 대신) |
| 사유 | 비용 절감 · 운영 부담 완화 (학습/2차) |
| 전제 | 미니 K8s/로컬에서 볼륨 안정성 확인 후 EKS 반영 |
| 참고 | RDS 11.8 사용 가능하나 비용 모니터링 필수 |

### D-004 — 사전 테스트 환경 (미확정)

| 항목 | 내용 |
|------|------|
| 후보 A | 크레딧으로 소형 EKS |
| 후보 B | EC2 1대 + minikube(경량 K8s) |
| 상태 | **팀 선택 필요** — EKS 본배포 직전 통과 게이트 |
| 다음 | 금요일 아키텍처 회의에서 A/B 확정 |

### D-005 — CI/CD To-Be 방향

| 항목 | 내용 |
|------|------|
| 결정 | GitHub Actions → ECR → Argo CD → EKS (CodeDeploy 대체) |
| 담당 | 현우 (빌드·GitOps) / 서이 (클러스터·Ingress) / 윤주 (이미지·Helm·DB) |

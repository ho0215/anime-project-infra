# Aniverse EKS 전환 계획서

| 항목 | 내용 |
|------|------|
| 프로젝트 | Aniverse (2차 — 컨테이너 · Kubernetes) |
| 문서 목적 | EKS 전환 범위, 역할, 일정, 우선순위 공유 |
| 작성 기준 | 멘토링 피드백 반영 |
| 계정 · 비용 | 현우 계정 사용, 비용 엔빵 |
| 관련 산출물 | [As-Is / To-Be](./architecture-as-is-to-be.md), [결정 로그](./decision-log.md), [트러블슈팅](./troubleshooting-log.md) |

---

## 1. 목표

### 1.1 한 줄 목표

EC2 · ASG · CodeDeploy 기반 구성을 **컨테이너화**하고 **Kubernetes(EKS)** 에 올려, 서비스가 **정상 동작**하는 것을 확인한다.

### 1.2 성공 기준

- [x] Django 앱이 Docker 이미지로 빌드된다.
- [x] 로컬 또는 미니 K8s(EC2 + minikube 등)에서 앱 + DB가 정상 동작한다.
- [x] EKS 클러스터가 기동되고, Ingress(ALB)를 통해 앱에 접근 가능하다.
- [x] DB는 **Pod(StatefulSet) + 볼륨**으로 동작하며, 백업/복구 전략이 문서화되어 있다.
- [x] GitHub Actions → ECR → (Argo CD) 배포 흐름의 뼈대가 동작한다.
- [x] As-Is(EC2) 코드는 git에 보존하고, To-Be(EKS)와 비교 가능하다.

### 1.3 핵심 원칙

| 원칙 | 설명 |
|------|------|
| 아키텍처 우선 | 서비스 이관보다 **아키텍처 확정**이 먼저다. |
| 동작 확인이 1순위 | 모니터링 · 보안 · 자동화보다 **K8s에서 정상 동작**이 최우선이다. |
| 비용 민감 | EKS 컨트롤 플레인 · 노드 · EBS 비용을 수시로 확인하고, 미사용 시 삭제한다. |
| 오픈소스 우선 | 모니터링 등은 AWS 유료 기능보다 Prometheus · Grafana 등 오픈소스를 우선 검토한다. |
| 계획 · 변경 기록 | 계획 변동 시 **사유**를 남기고, 트러블슈팅을 메모한다. |

---

## 2. 전환 범위

### 2.1 옮기는 것 (To-Be 중심)

| 영역 | As-Is | To-Be |
|------|--------|--------|
| 앱 런타임 | EC2 + Nginx + Daphne | Pod (Deployment) |
| 배포 | GitHub Actions → CodeDeploy | GitHub Actions → ECR → Argo CD / Helm |
| 스케일 | ASG | 노드 오토스케일 + 파드 HPA (개념 · 설정 분리) |
| 진입점 | ALB → 타깃 그룹 → EC2 | Ingress / Gateway → ALB → Pod |
| DB | RDS (MariaDB) | **DB Pod (StatefulSet) + PVC(EBS)** |
| 설정 | EC2 `.env` / Secrets | ConfigMap · Secret · (추후 External Secrets) |

### 2.2 유지 · 재사용 후보

- VPC / Subnet 등 네트워크 뼈대 (Terraform 유지 · 확장)
- (필요 시) ACM, WAF, Route53 — Ingress · ALB와 연동
- EC2/CodeDeploy 완성본은 **git 태그로 보존** (포트폴리오 · 롤백 스토리)

### 2.3 DB를 Pod로 두는 사유 (포트폴리오 · 발표용)

1. **비용 절감** — RDS 상시 비용 대비 학습/2차 환경에서 유리  
2. **운영 부담 완화** — 클러스터 안에서 앱과 동일 패턴으로 관리  
3. **전제** — 로컬/미니 K8s에서 볼륨(EBS CSI) 안정성을 확인한 뒤 이관  
4. 참고 — RDS 11.8은 아직 사용 가능하나, 비용 체크를 전제로 한다.

---

## 3. 역할 분담

> 멘토링: 네트워크와 컴퓨트가 연동되면 **합쳐서** 진행. Terraform 코드는 유지 · 확장.

| 파트 | 담당 | 주요 업무 |
|------|------|-----------|
| **GitOps & CI/CD** | 현우 | · GitHub Actions로 푸시 시 자동 빌드<br>· Argo CD로 GitOps 배포<br>· ECR 이미지 태그 자동 업데이트<br>· Kustomize / Helm 오버레이로 환경별 설정<br>· Argo ↔ 클러스터 · 계정 권한 연동 (네트워크와 협업) |
| **네트워크 & 컴퓨트** | 서이 | · Terraform으로 EKS 클러스터 생성<br>· 워커 노드 그룹 · 오토스케일링<br>· IAM (노드 / 파드)<br>· VPC CNI · 파드 네트워크<br>· Ingress / Gateway · 외부 트래픽<br>· PV/PVC · StorageClass · EBS CSI (비용 주의)<br>· (여유) ResourceQuota |
| **컨테이너화 & DB** | 윤주 | · Django / Nginx Dockerfile · 이미지 빌드<br>· Helm 차트로 앱 배포 패키지<br>· StatefulSet으로 DB 컨테이너<br>· RDS → 컨테이너 DB 마이그레이션<br>· 백업 / 복구 전략 |

### 협업 경계

- **서이 ↔ 현우:** Ingress(ALB), 클러스터 접근 권한, Argo가 바라보는 클러스터  
- **윤주 ↔ 현우:** 이미지 이름 · 태그, Helm values / env  
- **윤주 ↔ 서이:** PVC · StorageClass · DB Pod 스케줄링  

※ 팀 4명인 경우, 유민은 **네트워크 & 컴퓨트** 또는 **Ingress · ALB · Argo 연동**에 합류한다. (별도 4번째 대축은 두지 않음)

---

## 4. 우선순위

다 중요하나, **진행 순서**는 아래를 따른다.

| 순위 | 항목 | 설명 |
|------|------|------|
| 1 | **아키텍처** | As-Is / To-Be, 구성 요소, 비용 · 보안 초안 |
| 2 | **서비스 이관 · 동작 확인** | 컨테이너화 → 미니 K8s → EKS에서 정상 동작 |
| 3 | **모니터링** | Prometheus · Grafana (Helm, 오픈소스) |
| 4 | **보안 · 안정성** | 베이스 이미지, ECR 권한, (후순위) Private Endpoint · 클러스터 only |
| 5 | **자동화 고도화** | 이미지 태그 자동화, HPA / Cluster Autoscaler 문서화 |

### 오토스케일링

작업을 **두 갈래**로 인식 · 문서화한다.

1. **노드** 스케일 (클러스터 / 노드 그룹)  
2. **파드** 스케일 (HPA 등)  

“노드를 늘릴지, 파드를 늘릴지”를 아키텍처에 한 줄로 명시한다.

---

## 5. 사전 테스트 환경 (둘 중 하나)

| 옵션 | 내용 | 비고 |
|------|------|------|
| A | AWS 프리티어 · 크레딧으로 소형 EKS | 실환경과 동일, 컨트롤 플레인 비용 주의 |
| B | **EC2 1대 + minikube(경량 K8s)** | AWS와 유사 실습, 비용 상대적으로 낮음 |

**원칙:** EKS 본배포 **직전**에 선택한 환경에서 앱 + DB 통과 후 진행한다.  
크레딧 사용 시 Budgets/알람을 설정하고, 미사용 클러스터는 삭제한다.

---

## 6. 일정

| 기한 | 마일스톤 | 산출물 |
|------|----------|--------|
| **금요일까지** | 아키텍처 확정 | As-Is / To-Be 다이어그램, 결정 로그 |
| **~17일** | EKS 기동 · 서비스 동작 | 클러스터 UP, 앱/DB 응답, 기본 CD 뼈대 |
| **18일** | 발전 방향 회의 · 오후 멘토링 | 회고, 다음 과제 |
| **18일 이후** | 각자 포트폴리오 | 트러블슈팅, 비교(v1 EC2 vs v2 EKS) |

---

## 7. Phase별 실행 계획

### Phase A — 아키텍처 (지금 → 금요일) ★게이트

**공통**

- [x] As-Is (ALB · ASG · CodeDeploy · RDS …) 정리  
- [x] To-Be (EKS · Ingress · App Pod · DB StatefulSet · ECR · Argo) 정리  
- [x] Keep / Replace / Add 표  
- [x] 보안 초안: 베이스 이미지, ECR 접근 범위  
- [x] 비용 러프 추정 (컨트롤 플레인 + 노드 + EBS)  
- [x] env로 뺄 항목 초안 목록  

**역할**

- 서이: EKS · 노드 · 네트워크 · EBS CSI 박스  
- 윤주: 앱 · DB 컨테이너 · PVC  
- 현우: Actions → ECR → Argo 흐름  

**게이트:** 아키텍처 리뷰 통과 전에는 본격 이관하지 않는다. → **통과**

---

### Phase B — 로컬 / 미니 K8s 검증 (EKS 직전) ★게이트

**윤주**

- [x] Dockerfile 작성 · 이미지 빌드  
- [x] 앱 + DB를 compose 또는 minikube에서 기동  
- [x] 헬스체크 · 주요 기능 확인  
- [x] 볼륨 재시작 후 데이터 유지 확인  
- [x] Helm 차트 초안  

**서이**

- [x] 테스트 환경(옵션 A 또는 B) 준비  
- [x] Ingress · StorageClass 계획  

**현우**

- [x] Actions 빌드 파이프라인 뼈대  
- [x] 이미지 태그 규칙 초안  
- [x] env → ConfigMap/Secret 매핑 표  

**게이트:** 미니 K8s(또는 동등 환경)에서 앱 + DB 정상 동작. → **통과**

---

### Phase C — EKS 이관 (~17일) ★게이트

**서이**

- [x] Terraform EKS + 노드 그룹  
- [x] IAM · VPC CNI  
- [x] Ingress → ALB  
- [x] EBS CSI + StorageClass  
- [x] 오토스케일(노드) 설정 · 문서화  

**윤주**

- [x] Helm으로 app / db 배포  
- [x] 데이터 이관 · 백업/복구 문서  
- [x] StatefulSet 안정화  

**현우**

- [x] ECR 연동 · Actions 푸시  
- [x] Argo CD Application  
- [x] 환경별 overlay  
- [x] 권한 · GitOps 경로 정리  

**게이트:** 17일 — ALB(또는 동등)로 앱 응답, DB 연결 확인. → **통과**

---

### Phase D — 고도화 · 포트폴리오 (18일 이후)

우선순위 3→5 순으로 얇게 진행한다.

- [ ] Prometheus + Grafana (Helm) — 메트릭 · 대시보드 최소  
- [x] 베이스 이미지 · ECR 최소 권한 (+ Actions OIDC, Pod S3 IRSA)  
- [ ] (후순위) Private Endpoint, 클러스터 only 접근  
- [x] HPA vs 노드 스케일 차이 문서화 (Helm HPA + Cluster Autoscaler)  
- [x] 이미지 태그 자동화 (`sha-*` GitOps bump)  
- [ ] 언급 · 학습: SonarQube / Quality Gate, OpenTelemetry, Argo UI  
- [ ] 각자 포트폴리오 스토리 · 트러블슈팅 메모  

---

## 8. 보안 (단계적)

| 단계 | 내용 | 우선 |
|------|------|------|
| 기본 | 신뢰할 수 있는 **베이스 이미지**, 불필요 패키지 최소화 | 높음 |
| 기본 | ECR에 **해당 프로젝트(역할)만** 접근 | 높음 |
| 후순위 | EKS API · 이미지 pull **Private Endpoint** | 낮음 |
| 후순위 | **해당 클러스터에서만** 접근 가능하도록 제한 | 낮음 |

대기업형 DevOps는 보안까지, 소규모는 파이프라인 중심이지만, 본 프로젝트는 **동작 확인 다음**에 보안을 보강한다.

---

## 9. 모니터링 · 기타 (참고)

| 항목 | 방침 |
|------|------|
| 스택 | Grafana + Prometheus (Helm 차트 적용 후 세부 설정) |
| 메트릭 | 노드/파드 자원, (여유 시) 네트워크 in/out |
| 임계치 | 노드 · 파드 임계치 개념만 숙지 · 필요 시 최소 적용 |
| Argo CD | 애플리케이션 상태 · 배포 이력 확인 (DevOps) |
| OpenTelemetry | “현업에서 많이 쓴다” 수준으로 인지 |
| SonarQube | 코드 품질 · 취약점 / Quality Gate — 여유 시 파이프라인 검토 |
| 환경변수 | DB, Redis, Secret, 이미지 태그 등 **무엇을 env로 뺄지** 표로 관리 |

---

## 10. 노션 · 문서 운영

### 10.1 노션 구조 (권장)

```
Aniverse EKS 전환
├── 00. 목표 · 성공 기준 · 비용 원칙
├── 01. 아키텍처 (As-Is / To-Be)     ← 금요일 게이트
├── 02. 역할 · RACI
├── 03. 스프린트 보드 (Phase A~D)
├── 04. 결정 로그
├── 05. 트러블슈팅 메모
├── 06. 계획 변경 이력 (언제 · 왜)
└── 07. 포트폴리오 포인트 (18일 이후)
```

### 10.2 결정 로그에 남길 항목 예시

- 테스트 환경: 크레딧 EKS vs EC2+minikube  
- DB: RDS 유지 vs Pod 전환 (사유 포함)  
- 오토스케일: 노드 / 파드 각각의 목표  
- 계정 · 비용 분담  

### 10.3 트러블슈팅 로그

상세 기록: [`troubleshooting-log.md`](./troubleshooting-log.md)

- 일시 · 담당 · 환경  
- 증상 · 가설 · 원인 · 조치  
- 재발 방지 · 계획 변경 여부  
- Cursor에서 해결 시 「로그에 남겨줘」로 항목 추가  

---

## 11. 리스크 · 주의

| 리스크 | 대응 |
|--------|------|
| EKS 컨트롤 플레인 상시 과금 | 실습 후 노드 0(`scripts/eks-stop.sh`) 또는 클러스터 삭제 — [eks-start-stop.md](./eks-start-stop.md), Budgets 알람 |
| EBS · PV 비용 | 볼륨 크기 최소화, 미사용 PVC 정리 |
| RDS와 Pod DB 혼선 | To-Be는 Pod로 통일하고 문서에 명시 |
| 범위 확산 (메시, Karpenter 등) | Phase D 이전에는 최소 구성만 |
| As-Is 코드 유실 | EC2/CodeDeploy 버전 **git 태그** 유지 |

---

## 12. 포트폴리오 메시지 (초안)

> Aniverse v1은 EC2 · ASG · CodeDeploy로 운영했고, v2는 비용 · 운영 부담을 고려해 DB를 Pod로 두며 EKS · GitOps(Argo CD) · GitHub Actions로 이관했다. 아키텍처를 먼저 고정한 뒤 컨테이너 동작 확인을 최우선으로 진행했다.

---

## 13. 바로 할 일 (체크)

- [ ] 본 계획서를 노션에 옮기고 담당자 확인  
- [ ] 금요일까지 As-Is / To-Be 아키텍처 초안 합치기  
- [ ] 테스트 환경(A/B) 결정 · 결정 로그 기록  
- [ ] EC2/CodeDeploy 안정본 git 태그  
- [ ] AWS Budgets / 크레딧 잔액 확인  

---

*문서 버전: 1.0 · 멘토링 피드백 기준 초안*

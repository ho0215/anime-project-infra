# Aniverse V1V2 발표 — 작업 기준본 분석

**기준 파일 (앞으로 여기 기준):**
- `docs/presentation/ppt/Aniverse_V1V2_발표_working.pptx`
- 생성 스크립트: `make_aniverse_v1v2_ppt.py` · 다이어그램: `make_hybrid_diagrams.py`
- 슬라이드: **11장** · 13.333×7.5 in

---

## 슬라이드 맵 (실제 순서)

| # | 제목 | 유형 | 비고 |
|---|------|------|------|
| 1 | 표지 | 텍스트 | Aniverse / 팀 4명 |
| 2 | Architecture V1 정의 | 2×2 카드 | 정의·구현방식·배경·범위 |
| 3 | 시스템 구성도 · V1 | 이미지 | `hybrid_01_arch_v1_vpc.png` |
| 4 | V1 한계 · V2 목표 · V2 차별점 | 3열 | 관측 / 반영 / ASG 비용 |
| 5 | Architecture V2 정의 | 비전+기능 4칸 | |
| 6 | 시스템 구성도 · V2 | 이미지 | `hybrid_02_arch_v2_vpc.png` |
| 7 | Architecture V2의 강점 | 행 리스트 | 재현·스케일·DB·보안·관측 |
| 8 | 기능 · 운영 검증 기준 | 6카드 | health~알림 |
| 9 | 기술 스택 · V2 | **이미지** | `hybrid_09_tech_stack.png` |
| 10 | 데이터 흐름 · V2 | **이미지** | `hybrid_10_data_flow.png` |
| 11 | 향후 계획 · 3UP | 3열+AIOps | Unique에 AIOps |

---

## 슬라이드별 확정 문구

### 1. 표지
- **Aniverse**
- 통합 서브컬처 커뮤니티 사이트
- Architecture V1 → V2 · EKS · GitOps 전환
- https://aniverse.my
- Team: **김현우, 박서이, 김윤주, 강유민**

### 2. Architecture V1 정의
| 칸 | 내용 |
|----|------|
| V1 정의 | User → ALB → ASG/EC2(Nginx+Django) → RDS · EFS · S3 로 Aniverse 서비스를 운영하던 초기 클라우드 구성 |
| 구현 방식 | Terraform으로 VPC·ALB·ASG 구성, CodeDeploy / Actions로 EC2 배포 |
| 개발 배경 | 통합 서브컬처 사이트 안정 서비스 위해 **온프레미스 → AWS**, EC2 기반 3-tier 구축 |
| 구현 범위 | HTTPS(ACM)·WAF·Redis·미디어 S3까지 운영 가능 형태 완료 |

### 3. 구성도 V1
- 이미지 슬라이드 (VPC 스타일 구성도)

### 4. V1 한계 / V2 목표 / V2 차별 (3×3)

**V1 한계**
1. 모니터링이 한눈에 안 보임 — 메트릭·로그·배포 상태 분산
2. 수정 → 서비스 반영이 어려움 — EC2/에이전트에 묶임
3. ASG만으로 늘렸다 줄이기 — 인스턴스 단위·상시 용량 비용 낭비

**V2 목표**
1. 관측을 한곳에 — Prom/Grafana·Loki
2. 변경하면 즉시 배포 — 이미지 + GitOps(Argo) Synced
3. 필요한 만큼만 스케일 — 노드·파드 · start/stop

**V2 차별**
1. 관측 스택 — Prom·Grafana·Loki, Alert/Tempo 확장
2. Actions → ECR → Argo — sha-* bump + sync
3. EKS + DB Pod — 노드/파드 스케일 + PVC

### 5. Architecture V2 정의
- **비전:** EKS 위 GitOps로 재현 가능 운영, 데이터·관측·보안 한 사이클
- **주요 기능:** ALB Ingress·HTTPS / EKS web·db Pod / 백업·관측 / Actions→ECR→Argo

### 6. 구성도 V2
- 이미지 슬라이드

### 7. Architecture V2의 강점
| 항목 | 내용 → 반영 |
|------|-------------|
| 배포 재현 | 동일 이미지·매니페스트 → Actions → ECR → Argo |
| 스케일 분리 | 노드 / 파드 HPA 분리 → EKS + HPA |
| DB 비용 | RDS 상시 대신 학습용 영구 볼륨 → StatefulSet + PVC |
| 보안 | 장기 키 금지 · ARN 전수 교체 → OIDC · IRSA |
| 관측 | 메트릭·로그 기본 포함 → Prom / Grafana / Loki |

### 8. 검증 기준
| 항목 | 검증 | 방법 | 결과 |
|------|------|------|------|
| 웹 health | HTTPS 200 | curl/브라우저 | 충족 |
| DB 시드 | restore 후 목록 UI | minTables+seed_rows | 충족 |
| GitOps | tag bump → Synced | Actions+Argo | 충족 |
| 미디어 | destroy 후 Sync media | S3 media/ | 충족 |
| 관측 | 대시보드 조회 | 클러스터 메트릭 | 구성 |
| 알림/트레이싱 | AlertManager·Tempo | 다음 단계 | 예정 |

### 9. 기술 스택 (이미지)
6칸 아이콘 맵:
- 앱·런타임: Django · Nginx · Docker/Helm
- 오케스트레이션: EKS · MariaDB STS · EBS PVC
- 스토리지: S3 media / static / db-backups
- CI/CD·GitOps: Actions · ECR · Argo CD
- 인증·IaC: GitHub OIDC · Terraform · Secrets/IRSA
- 관측: Prometheus · Grafana · Loki

### 10. 데이터 흐름 (이미지)
1. 서비스: Users → ALB → web Pod → MariaDB → EBS PVC (eks-stop 시 PVC 유지)
2. destroy 후 시드: GitHub SQL → restore Job → MariaDB
3. 주기 백업: MariaDB → CronJob → S3 db-backups/
4. 미디어: web Pod → S3 media/ (DB 아님 · destroy 시 Sync media)
주의: terraform destroy = PVC+S3 삭제

### 11. 향후 3UP
- **Unique Up:** 관측 고도화 · OIDC 축소 · 백업 드릴 · **AIOps(self-healing)**
- Complete / Performance: Loki·시드 게이트·런북 / start-stop·대비 설명·장애 데모

---

## 앞으로 작업 규칙

1. 편집·재생성은 **이 11장 구조·문구**를 기준으로 한다.
2. 소스 오브 트루스 PPT: `ppt/Aniverse_V1V2_발표_working.pptx`
3. 버전 올리면 `Aniverse_V1V2_발표_vN.pptx`로 쌓되, working도 같이 갱신한다.
4. 구성도·스택·흐름 PNG: `images/hybrid/hybrid_01_*`, `hybrid_02_*`, `hybrid_09_tech_stack.png`, `hybrid_10_data_flow.png`

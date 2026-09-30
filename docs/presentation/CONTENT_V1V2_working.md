# Aniverse V1V2 발표 — 작업 기준본 분석

**기준 파일 (앞으로 여기 기준):**
- `docs/presentation/ppt/Aniverse_V1V2_발표_working.pptx`
- 생성 스크립트: `make_aniverse_v1v2_ppt.py` · 다이어그램: `make_hybrid_diagrams.py`
- 슬라이드: **16장** · 13.333×7.5 in

---

## 슬라이드 맵 (실제 순서)

| # | 제목 | 유형 | 비고 |
|---|------|------|------|
| 1 | 표지 | 텍스트 | Aniverse / 팀 4명 |
| 2 | Architecture V1 | 2×2 카드 | 구성·배포·배경·운영 범위 |
| 3 | 시스템 구성도 · V1 | 이미지 | `hybrid_01_arch_v1_vpc.png` |
| 4 | V1 한계 · V2 목표 · V2 차별점 | 3열 | 관측 / 배포 / 확장 |
| 5 | Architecture V2 | 비전+기능 4칸 | |
| 6 | 시스템 구성도 · V2 | 이미지 | `hybrid_02_arch_v2_vpc.png` |
| 7 | Architecture V2 · 배포와 데이터 | 3행 | DB Pod · sha 태그 · 시드 |
| 8 | Architecture V2 · 인증과 DNS | 2행 | Zero-Key(OIDC·SSO) · DNS 유지 |
| 9 | 기능 · 운영 검증 기준 | 6카드 | health~Slack 알림 |
| 10 | 기술 스택 · V2 | **이미지** | `hybrid_09_tech_stack.png` |
| 11 | 데이터 흐름 · V2 | **이미지** | `hybrid_10_data_flow.png` |
| 12 | 앞으로 보완할 점 | 3열 | 운영 고도화 · 완성도 · 발표 |
| 13 | 트러블슈팅 · 노드를 껐는데 다시 켜졌다 | 3열 | 증상 / 원인 / 해결 |
| 14 | 트러블슈팅 · EKS | 3행 | HPA · 생성 순서 · 시크릿 값 |
| 15 | 트러블슈팅 · DB · 관측 | 3행 | 백업 0바이트 · Alloy 한도 · Slack |
| 16 | V2 일정 · 일자별 | 이미지 | `images/v2_schedule_by_day.png` |

---

## 슬라이드별 확정 문구

### 1. 표지
- **Aniverse**
- 통합 서브컬처 커뮤니티 사이트
- Architecture V1 → V2 · EKS · GitOps 전환
- https://aniverse.my
- Team: **김현우, 박서이, 김윤주, 강유민**

### 2. Architecture V1
| 칸 | 내용 |
|----|------|
| 구성 | ALB → EC2(Nginx+Django) → RDS, EFS, S3 |
| 배포 | Terraform으로 인프라 구성, Actions와 CodeDeploy로 EC2 배포 |
| 전환 배경 | 온프레미스 서비스를 AWS의 EC2 기반 3-tier로 이전 |
| 운영 범위 | HTTPS, WAF, Redis, S3 미디어 저장 |

### 3. 구성도 V1
- 이미지 슬라이드 (VPC 스타일 구성도)

### 4. V1 한계 / V2 목표 / V2 차별 (3×3)

**V1 한계**
1. 상태를 한눈에 보기 어려움 — 메트릭·로그·배포 상태 분산
2. 변경 반영이 느리고 복잡함 — EC2와 배포 에이전트에 의존
3. 인스턴스 단위로만 확장 — 비용을 세밀하게 조절하기 어려움

**V2 목표**
1. 메트릭과 로그를 한곳에서 확인
2. 커밋부터 배포까지 자동화
3. 노드와 파드를 따로 조절

**V2 차별**
1. 통합 관측 — Prometheus·Alloy·Loki와 Slack 알림
2. GitOps 배포 — Actions → ECR → Argo CD
3. EKS + DB Pod — 앱과 DB를 Kubernetes에서 운영

### 5. Architecture V2
- **비전:** 배포·데이터 복구·관측·인증을 하나의 운영 흐름으로 구성
- **주요 기능:** ALB Ingress·HTTPS / EKS web·db Pod / 백업·관측 / Actions→ECR→Argo

### 6. 구성도 V2
- 이미지 슬라이드

### 7–8. Architecture V2 상세내용
| # | 항목 | 내용 |
|---|------|------|
| ① | DB를 클러스터 안으로 | MariaDB StatefulSet + PVC |
| ① | 배포 이미지도 Git으로 관리 | ECR `sha-*` + Helm 태그 갱신 |
| ① | 재구축 후 데이터 복구 | Git SQL → restore Job → DB 시드 |
| ② | 장기 키 없는 Zero-Key 구성 | 파드·CI는 OIDC, 사람은 SSO |
| ② | 클러스터를 지워도 도메인 유지 | Route53 영역을 삭제 대상에서 제외 |

### 9. 검증 기준
| 항목 | 검증 | 방법 | 결과 |
|------|------|------|------|
| 웹 접속 | HTTPS 200 | curl·브라우저 | 확인 |
| DB 데이터 | 목록 데이터 표시 | 테이블 수·시드 행 | 확인 |
| GitOps | Git 태그와 배포 이미지 일치 | Actions·Argo CD | 확인 |
| 미디어 | 재구축 후 이미지 표시 | S3 media 경로 | 확인 |
| 관측 | 메트릭·로그 조회 | Prometheus·Loki | 구성 |
| 알림 | AlertManager 알림 수신 | Slack 채널 | 확인 |

### 10. 기술 스택 (이미지)
6칸 아이콘 맵:
- 앱·런타임: Django · Daphne · Docker/Helm
- 오케스트레이션: EKS · MariaDB STS · EBS PVC
- 스토리지: S3 media / static / db-backups
- CI/CD·GitOps: Actions · ECR · Argo CD
- 인증·IaC: GitHub OIDC · Terraform · Secrets/IRSA
- 관측: Prometheus · Alloy · Loki

### 11. 데이터 흐름 (이미지)
1. 서비스: Users → ALB → web Pod → MariaDB → EBS PVC (eks-stop 시 PVC 유지)
2. destroy 후 시드: GitHub SQL → restore Job → MariaDB
3. 주기 백업: MariaDB → mariadb-dump CronJob → S3 db-backups/
4. 미디어: web Pod → S3 media/ (DB 아님 · destroy 시 Sync media)

### 12. 앞으로 보완할 점
- **운영 고도화:** 트레이싱 · OIDC 권한 최소화 · 정기 복구 훈련 · 반복 장애 자동 복구
- **완성도:** 시드 검증 자동화 · 운영 런북 · 계정 이관 체크리스트
- **발표·시연:** start/stop · V1/V2 비교 · 대표 장애 해결 과정

### 13. 트러블슈팅 · 노드를 껐는데 다시 켜졌다
- 증상: 중지 작업은 성공했지만 EC2 워커는 계속 실행
- 원인: desired만 0으로 바꿔 Autoscaler가 노드를 다시 생성
- 해결: ASG Launch 중지, 인스턴스 0대 확인, NAT 함께 중지

### 14. 트러블슈팅 · EKS
- HPA가 늘린 파드가 다시 1개로 줄어듦 — replicas 고정값을 제거
- 새 계정에서 일부 리소스가 생성되지 않음 — NAT·라우팅 생성 순서 조정
- 기존 DB 비밀번호가 약한 기본값일 가능성 — DB와 Secrets Manager 값을 함께 교체

### 15. 트러블슈팅 · DB · 관측
- S3 DB 백업이 0바이트 — DB 파드 안에서 mariadb-dump 실행
- Alloy가 일부 노드에서 실행되지 않음 — max-pods 상향 후 노드 재생성
- Slack 알림이 오지 않음 — 웹훅 시크릿 마운트와 api_url_file 연결

---

## 앞으로 작업 규칙

1. 편집·재생성은 **이 16장 구조·문구**를 기준으로 한다.
2. 소스 오브 트루스 PPT: `ppt/Aniverse_V1V2_발표_working.pptx`
3. 버전 올리면 `Aniverse_V1V2_발표_vN.pptx`로 쌓되, working도 같이 갱신한다.
4. 구성도·스택·흐름 PNG: `images/hybrid/hybrid_01_*`, `hybrid_02_*`, `hybrid_09_tech_stack.png`, `hybrid_10_data_flow.png`

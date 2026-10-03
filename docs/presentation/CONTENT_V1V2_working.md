# Aniverse V1V2 발표 — 작업 기준본 분석

**기준 파일 (앞으로 여기 기준):**
- `docs/presentation/ppt/Aniverse_V1V2_발표_working.pptx`
- 생성 스크립트: `make_aniverse_v1v2_ppt.py` · 다이어그램: `make_hybrid_diagrams.py` · 일정: `make_v2_schedule.py`
- 슬라이드: **18장** · 13.333×7.5 in

---

## 슬라이드 맵 (실제 순서)

| # | 제목 | 유형 | 비고 |
|---|------|------|------|
| 1 | 표지 | 텍스트 | Aniverse / 팀 4명 |
| 2 | Architecture V1 | 2×2 카드 | 구성·배포·배경·운영 범위 |
| 3 | 시스템 구성도 · V1 | 이미지 | `hybrid_01_arch_v1_vpc.png` |
| 4 | V1 한계 · V2에서 바꾼 점 · V2의 핵심 | 3열 | 제목·칼럼 일치 |
| 5 | Architecture V2 | 비전+기능 4칸 | |
| 6 | 시스템 구성도 · V2 | 이미지 | Argo 아이콘 · Actions→ECR→Argo→EKS · Redis/ESO/OIDC |
| 7 | Architecture V2 · 배포와 데이터 | 3행 | DB Pod · sha 태그 · 시드 |
| 8 | Architecture V2 · 보안과 DNS | 3행 | Zero-Key(OIDC·SSO) · WAF · DNS · 이관 한 줄 |
| 9 | 기능 · 운영 검증 기준 | 6카드 | 확인/구성 기준 설명 |
| 10 | 기술 스택 · V2 | **이미지** | Prom/Grafana/Tempo/Alert/ESO |
| 11 | 데이터 흐름 · V2 | **이미지** | `hybrid_10_data_flow.png` |
| 12 | 앞으로 보완할 점 | 2열 | 트레이싱은 성과로 이동 · 발표·시연 칸 제거 |
| 13 | 부하테스트 · 트레이싱 | 3열 | HPA 2→4 · /works 병목 · Redis Timeout |
| 14 | 트러블슈팅 · GitOps · CI/CD | 3행 | 현우 |
| 15 | 트러블슈팅 · EKS | 3행 | 서이 (HPA·생성순서·비밀번호) |
| 16 | 트러블슈팅 · DB · 관측 | 3행 | 윤주 |
| 17 | V2 일정 · 일자별 | 이미지 | 9/29 RBAC · DB·관측 일정 보강 |
| 18 | Q & A | 텍스트 | 팀 역할 한 줄 |

---

## 슬라이드별 확정 문구

### 8. Zero-Key
- OIDC(워크로드): 파드·CI Access Key 차단
- SSO(사람): 장기 키 없이 임시 자격증명
- 결과: Zero-Key 구성
- 이관: 계정 접근 제한으로 복구가 어려워 팀원 계정으로 이관하며 SSO·OIDC로 전환 (원인은 단정하지 않음)

### 12. 앞으로 보완할 점
- 운영 고도화: OIDC 축소 · 복구 훈련(S3 경로 포함) · AIOps · 비용(노드·NAT 중지, 상시 RDS 제거)
- 완성도: 런북 · 이관 체크리스트 · /works 병목·Redis Timeout 해소

### 13. 부하 · 트레이싱
- 확인: HPA 2→4, Grafana에서 실제 요청 trace 조회, AlertManager Slack 알림 수신
- 발견: /works 최대 ~2.91초(팀 측정), Tempo 병목 구간, ASGI extra 누락 보완
- 과제: Redis TimeoutError 수정 후 재검증

### 15. 트러블슈팅 · EKS (서이)
- HPA replicas 충돌 (9/15)
- Terraform 생성 순서 (9/22)
- DB 비밀번호 로테이션 (9/29)

### 17. 일정
- 9/29 EKS: RBAC 설정
- DB·관측: 9/18 백업 IRSA, 9/21 Loki·Alloy·Alert·Tempo 설정, 9/23 DB dump·Slack
- 성능·추적: 9/28 OTel·안티어피니티, 9/29 Tempo 배포·파드 분산, 10/1 부하테스트·ASGI trace

---

## 앞으로 작업 규칙

1. 편집·재생성은 **이 18장 구조·문구**를 기준으로 한다.
2. 소스 오브 트루스 PPT: `ppt/Aniverse_V1V2_발표_working.pptx`
3. 버전 올리면 `Aniverse_V1V2_발표_vN.pptx`로 쌓되, working도 같이 갱신한다.
4. 생성: `python3 make_hybrid_diagrams.py` → `python3 make_v2_schedule.py` → `python3 make_aniverse_v1v2_ppt.py`

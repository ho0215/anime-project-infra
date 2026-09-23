# 하이브리드 발표 대본 (5~7분)

PPT: `ppt/Aniverse_하이브리드_EKS.pptx`  
구성도: `images/hybrid/*.png` (AI 생성) · 생성 스크립트 `make_hybrid_ppt.py`

## 시간 배분
| 구간 | 시간 | 슬라이드 |
|------|------|----------|
| 표지·목차·서비스·역할 | 1분 | 1–4 |
| 아키텍처 v1 2장 · v2 · 왜 EKS | 1분 40초 | 5–8 |
| 전환 경로 · 워크로드 · GitOps · 데이터 | 2분 | 9–12 |
| 관측 · 운영 | 50초 | 13–14 |
| 이슈 (Missing · Block/이관) | 1분 10초 | 15–16 |
| Before/After · 다음 | 40초 | 17–18 |

## 멘트 포인트
- **5 아키텍처 v1 (1):** 손가락으로 User→ALB→EC2→RDS/EFS/S3 전체 한 바퀴
- **6 아키텍처 v1 (2):** 위=요청 처리, 아래=Actions→CodeDeploy 배포 흐름
- **7 아키텍처 v2:** EKS · Ingress · Pod · Argo 한 바퀴
- **4 역할:** 윤주=Docker/Helm/DB/관측, 현우=Actions/Argo/OIDC
- **8 왜 EKS:** DB Pod는 비용·학습 — RDS 대체가 목표였음
- **10 워크로드:** entrypoint migrate · EKS 1/1 Running
- **12 데이터:** CronJob→`db-backups/` · restore Job · media는 S3 별도
- **13 관측:** Prom+Grafana 완료 · Loki/Alloy 구성 · Alert/Tempo는 다음
- **15 Missing:** sync-wave vs SSA — 증상 같아도 원인 분기
- **16 Block:** 표면 start 실패 ≠ 키 유출 · 이관 후 ARN 전수 교체
- **18 다음:** Loki 설치 마무리 · AlertManager · Tempo/OTel

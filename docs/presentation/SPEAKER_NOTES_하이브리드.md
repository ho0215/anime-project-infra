# 하이브리드 발표 대본 (5~7분)

PPT: `ppt/Aniverse_하이브리드_EKS.pptx`  
구성도: `images/hybrid/*.png` (AI 생성) · 생성 스크립트 `make_hybrid_ppt.py`

## 시간 배분
| 구간 | 시간 | 슬라이드 |
|------|------|----------|
| 표지·목차·서비스·역할 | 1분 | 1–4 |
| As-Is / To-Be / 왜 EKS | 1분 20초 | 5–7 |
| 전환 경로 · 워크로드 · GitOps · 데이터 | 2분 | 8–11 |
| 관측 · 운영 | 50초 | 12–13 |
| 이슈 (Missing · Block/이관) | 1분 20초 | 14–15 |
| Before/After · 다음 | 40초 | 16–17 |

## 멘트 포인트
- **4 역할:** 윤주=Docker/Helm/DB/관측, 현우=Actions/Argo/OIDC
- **7 왜 EKS:** DB Pod는 비용·학습 — RDS 대체가 목표였음
- **9 워크로드:** entrypoint migrate · EKS 1/1 Running
- **11 데이터:** CronJob→`db-backups/` · restore Job · media는 S3 별도
- **12 관측:** Prom+Grafana 완료 · Loki/Alloy 구성 · Alert/Tempo는 다음
- **14 Missing:** sync-wave vs SSA — 증상 같아도 원인 분기
- **15 Block:** 표면 start 실패 ≠ 키 유출 · 이관 후 ARN 전수 교체
- **17 다음:** Loki 설치 마무리 · AlertManager · Tempo/OTel

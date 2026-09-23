# 하이브리드 발표 대본 (5~7분)

PPT: `ppt/Aniverse_하이브리드_EKS_vN.pptx` (최신 = **v5**)  
구성도: `images/hybrid/*.png` · 생성 `make_hybrid_ppt.py`

**아키텍처 그림 규칙**
- 스타일: 강사용 **Terraform 인프라 구성 (1)** VPC 구성도와 동일  
  (AWS 아이콘 · VPC 점선 · Public/Private 서브넷 · 흐름 요약)
- **버전당 1장** (v1 한 장, v2 한 장)

## 시간 배분
| 구간 | 시간 | 슬라이드 |
|------|------|----------|
| 표지·목차·서비스·역할 | 1분 | 1–4 |
| 아키텍처 v1 · v2 · 왜 EKS | 1분 20초 | 5–7 |
| 전환 경로 · 워크로드 · GitOps · 데이터 | 2분 | 8–11 |
| 관측 · 운영 | 50초 | 12–13 |
| 이슈 (Missing · Block/이관) | 1분 20초 | 14–15 |
| Before/After · 다음 | 40초 | 16–17 |

## 멘트 포인트
- **5 아키텍처 v1:** VPC 안에서 User→ALB→EC2→RDS 한 바퀴
- **6 아키텍처 v2:** 같은 틀에서 EKS Pod · Argo · ECR
- **4 역할:** 윤주=Docker/Helm/DB/관측, 현우=Actions/Argo/OIDC
- **7 왜 EKS:** DB Pod는 비용·학습
- **9~12:** 워크로드·데이터·관측 (윤주)
- **14~15:** Missing / Block·이관
- **17 다음:** Loki · Alert · Tempo

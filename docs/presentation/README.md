# Aniverse 발표자료 (강사용)

온프레미스 3-tier → AWS · **5~7분** 평가용.

## 바로 쓰기

| 파일 | 용도 |
|------|------|
| **`ppt/Aniverse_발표_강사용.pptx`** | 발표 PPT (온프렘→AWS 강사용) |
| **`ppt/Aniverse_V1V2_발표_vN.pptx`** | NunSub 구조 참고 · V1→V2 발표용 (권장) |
| **`ppt/Aniverse_하이브리드_EKS_vN.pptx`** | 이전 하이브리드 상세판 |
| **`VIEW_강사발표.html`** | 브라우저 요약 |
| **`SPEAKER_NOTES_강사.md`** | 강사용 멘트 |
| **`SPEAKER_NOTES_하이브리드.md`** | 하이브리드 멘트 |

EKS AS-IS 한 장 구성도: `docs/aniverse-eks-architecture-as-is.png` (별도 문서)

## 다시 만들기

```bash
cd docs/presentation
python3 make_aws_overview_diagram.py       # 02 VPC
python3 make_terraform_modules_diagram.py  # 03 모듈 맵
python3 make_instructor_diagrams.py        # 01, 05~09 (+ 02/03 호출)
python3 make_instructor_ppt.py             # ppt/Aniverse_발표_강사용.pptx
python3 make_instructor_view.py            # VIEW_강사발표.html
python3 make_hybrid_diagrams.py            # images/hybrid/*.png (PIL+한글 폰트)
python3 make_hybrid_ppt.py                 # ppt/Aniverse_하이브리드_EKS_vN.pptx (버전 자동 +1)
```

하이브리드 구성도: `images/hybrid/hybrid_*.png` (`make_hybrid_diagrams.py`, 시스템 한글 폰트).  
PPT 템플릿: navy(#0A1128) + cyan(#00AEEF) 액센트 라인 · 큰 제목 · 구성도는 콘텐츠 영역 중앙 배치.  
아키텍처 **v1·v2는 각 1장**. 재생성 시 `Aniverse_하이브리드_EKS_vN.pptx` 로 버전 증가.
## 이미지 (`images/instructor/`)

| 파일 | 내용 |
|------|------|
| `01_onprem_3tier.png` | 온프렘 3-Tier |
| `02_aws_overview.png` | AWS VPC 아키텍처 |
| `03_terraform_modules.png` | Terraform 모듈 계층 |
| `04_github_actions.png` | CI/CD Pipeline |
| `05_ops_security.png` | 운영·보안 |
| `06_https_waf.png` | HTTPS / WAF 경로 |
| `07_aws_github_stack.png` | AWS · GitHub 스택 |
| `08_storage_roles.png` | S3 · EFS · RDS |
| `09_team_roles.png` | 팀 역할 |

아이콘: `images/icons/` (AWS Architecture Icons + GitHub 마크)  
원본 소스: `images/sources/`

## 역할 요약

| 담당 | 역할 | 모듈 |
|------|------|------|
| 박서이 | Network & Security | network / security / nat |
| 강유민 | Compute & Traffic | compute / alb |
| 김윤주 | Data & Storage | database / storage |
| 김현우 | DevOps & CI/CD | environments/dev · cicd · Actions |

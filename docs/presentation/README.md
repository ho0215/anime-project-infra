# Aniverse 발표자료 — 통합본

## 바로 보기 (이것만)

| 파일 | 용도 |
|------|------|
| **`VIEW.html`** | 브라우저 더블클릭 (추천, **그림 포함 단일 파일**) |
| **`ppt/Aniverse_발표_통합.pptx`** | PowerPoint |

```bash
# PPT 다시 만들기
cd docs/presentation
python3 generate_ppt.py
```

`slides.html` 은 `VIEW.html` 로 자동 이동합니다.

---

## 발표 흐름 (9장)

1. 한 줄 스토리  
2. Before → After 매핑  
3. AWS 팀 역할 (서이/유민/윤주/현우)  
4. 앱 담당 ↔ 클라우드 담당  
5. 전체 아키텍처 이미지  
6. Terraform 모듈  
7. CI/CD  
8. 트러블슈팅 (기존+최근 개선)  
9. 마무리 멘트  

---

## AWS 역할 요약

| 담당 | 역할 | 모듈 |
|------|------|------|
| 박서이 | Network & Security | network / security / nat |
| 강유민 | Compute & Traffic | compute / alb |
| 김윤주 | Data & Storage | database / storage |
| 김현우 | DevOps & CI/CD | environments/dev · cicd · Actions |

---

## 참고 파일

| 경로 | 설명 |
|------|------|
| `PRESENTATION.md` | 대본·표 상세 |
| `images/*.png` | 기존 아키텍처·CI/CD·모듈·트러블 이미지 |
| `*.drawio` | 선택(상세 편집용). **기본은 VIEW.html/PPT** |

자세한 대본은 `PRESENTATION.md` 참고.

## 강사 평가용 발표 (5~7분) — 최신

| 파일 | 용도 |
|------|------|
| **`ppt/Aniverse_발표_강사용.pptx`** | 발표 PPT (목차 고정) |
| **`VIEW_강사발표.html`** | 브라우저 요약본 |
| **`SPEAKER_NOTES_강사.md`** | 슬라이드별 멘트·시간 배분 |

주제: 온프레미스 3-tier → AWS  
기준: 청중이 **왜 중요한지** 바로 이해

### 강사용 다이어그램 다시 만들기

구성도는 **AWS Architecture Icons**(PlantUML 배포본)과 **GitHub / Actions / Terraform** 공식 마크를 사용합니다.

```bash
cd docs/presentation
python3 make_instructor_diagrams.py   # images/instructor/*.png
python3 make_instructor_ppt.py        # ppt/Aniverse_발표_강사용.pptx
python3 make_instructor_view.py       # VIEW_강사발표.html
```

| 이미지 | 내용 |
|--------|------|
| `01_onprem_3tier.png` | 온프렘 3-Tier (Nginx/Django/RDS 아이콘) |
| `02_aws_overview.png` | AWS 아키텍처 개요 |
| `03_terraform_modules.png` | Terraform 모듈 맵 |
| `04_github_actions.png` | CI/CD Pipeline (GitHub + AWS 아이콘) |
| `05_ops_security.png` | CI/CD·HA·모니터링·보안 |
| `06_https_waf.png` | Route53 → WAF → ACM/ALB → EC2 |
| `07_aws_github_stack.png` | 기술 스택 (AWS·GitHub, Terraform 전에 배치) |
| `08_storage_roles.png` | S3·EFS·RDS 역할 |
| `09_team_roles.png` | 팀 역할 + 담당 AWS 서비스 |


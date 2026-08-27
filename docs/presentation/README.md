# Aniverse 발표자료 — 통합본

## 바로 보기 (이것만)

| 파일 | 용도 |
|------|------|
| **`VIEW.html`** | 브라우저 더블클릭 (추천) |
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

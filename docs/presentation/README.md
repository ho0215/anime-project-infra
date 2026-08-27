# 발표 자료 — 보는 방법 (쉬운 버전)

draw.io는 쓰지 마세요. 아래 둘 중 하나로 보면 됩니다.

## 1) 브라우저 HTML (추천)

파일: **`VIEW.html`**

1. 탐색기에서 `docs/presentation/VIEW.html` 더블클릭  
2. Chrome / Edge 로 열림  
3. 위에서 아래로 스크롤만 하면 됨  
4. PPT용으로 쓰려면 `Ctrl+P` → **PDF로 저장** 또는 화면 캡처

포함 내용: 한줄 스토리 · Before/After · 팀 역할 4칸 · 아키텍처 · CI/CD · 발표 멘트

## 2) PowerPoint 파일

```bash
cd docs/presentation
python3 make_easy_ppt.py
```

생성 위치: **`ppt/Aniverse_발표.pptx`**  
이 파일을 PowerPoint / Google 슬라이드에서 열면 됩니다.

---

## (참고) 예전 파일

| 파일 | 비고 |
|------|------|
| `*.drawio` | 보기 어려움 → `VIEW.html` / PPT 사용 권장 |
| `images/*.png` | 기존 아키텍처 그림 (있으면 PPT에 추가 삽입 가능) |
| `PRESENTATION.md` | 대본 텍스트 |

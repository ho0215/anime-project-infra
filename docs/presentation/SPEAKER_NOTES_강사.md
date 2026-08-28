# 강사용 발표 대본 (5~7분)

PPT: `ppt/Aniverse_발표_강사용.pptx`  
HTML: `VIEW_강사발표.html`

## 시간 배분
| 구간 | 시간 | 슬라이드 |
|------|------|----------|
| 표지·목차·역할 | 1분 | 1–3 |
| 온프렘 어려움 | 50초 | 4–5 |
| 기술 스택 | 25초 | 6 |
| Terraform + Data | 1분 40초 | 7–11 |
| Actions | 50초 | 12–13 |
| CI/CD·HA·보안 | 40초 | 14–15 |
| HTTPS · WAF | 35초 | 16–17 |
| 트러블슈팅 | 40초 | 18 |
| 마무리 | 20초 | 19 |

구성도 슬라이드는 AWS Architecture Icons + GitHub 공식 마크를 사용합니다.

## 말할 때 포인트 (PPT에는 안 적음)
- 구조 그림은 **손가락으로 흐름을 따라가며** 설명
- 슬라이드 6: **왼쪽 AWS / 오른쪽 GitHub**만 가리키며 한 바퀴 (Terraform 전 도구 지도)
- 슬라이드 9: Remote State 선구축 → State Lock으로 **동시 작업**
- 슬라이드 9 계층별: Security = ALB/App/NAT/DB/EFS/Redis/endpoints SG
- 슬라이드 10: 구성 요소 네 칸
- 슬라이드 11: **RDS=글/회원 데이터, EFS=공유 파일, S3=이미지·배포 객체** 한 문장씩
- 슬라이드 15 보안: SG + **DB subnet NACL** + Secrets + HTTPS/WAF
- 7번: **HTTPS=자물쇠(암호화)**, **WAF=문지기(공격·과도한 요청 차단)**
- 슬라이드 17: 모듈명/규칙명 대신 “무엇을 했는지”만 말하기
- **슬라이드 18 트러블슈팅** — 각 항목 **상황→문제→선택→역할→결과** 순서로 말하기
  - ① NAT: network+NAT 통합 → security **순환 의존** → **3모듈 분리**
  - ② 키 노출: `.env` 노출 → AWS **자동 격리** → 키 교체·삭제  
    → **멘트만:** 장기 액세스 키 대신 **GitHub OIDC 연동은 진행 중** (완료 아님)
  - ③ DynamoDB: 팀 **S3 tfstate 공유** → 동시 apply 위험 → **State Lock**  
    → “앱 DB가 아니라 **Terraform 자물쇠**” (스토리 A)

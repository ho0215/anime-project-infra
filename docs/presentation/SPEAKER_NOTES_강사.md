# 강사용 발표 대본 (5~7분)

PPT: `ppt/Aniverse_발표_강사용.pptx`  
HTML: `VIEW_강사발표.html`

## 시간 배분
| 구간 | 시간 | 슬라이드 |
|------|------|----------|
| 표지·목차·역할 | 1분 | 1–3 |
| 온프렘 어려움 | 50초 | 4–5 |
| Terraform + Data | 1분 40초 | 6–10 |
| Actions | 50초 | 11–12 |
| CI/CD·HA·보안 | 40초 | 13–14 |
| HTTPS · WAF | 40초 | 15–16 |
| 마무리 | 20초 | 17 |

## 말할 때 포인트 (PPT에는 안 적음)
- 구조 그림은 **손가락으로 흐름을 따라가며** 설명
- 슬라이드 8: Remote State 선구축 → State Lock으로 **동시 작업**
- 슬라이드 8 계층별: Security = ALB/App/NAT/DB/EFS/Redis/endpoints SG
- 슬라이드 9: 구성 요소 네 칸
- 슬라이드 10: **RDS=글/회원 데이터, EFS=공유 파일, S3=이미지·배포 객체** 한 문장씩
- 슬라이드 14 보안: SG + **DB subnet NACL** + Secrets + HTTPS/WAF
- 6번: **HTTPS=암호화**, **WAF=차단·Rate limit**

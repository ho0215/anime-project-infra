# Aniverse V1→V2 발표 대본 (작업 기준본 · 18장)

PPT: `ppt/Aniverse_V1V2_발표_working.pptx`  
내용 문서: `CONTENT_V1V2_working.md`  
생성: `python3 make_hybrid_diagrams.py` → `python3 make_v2_schedule.py` → `python3 make_aniverse_v1v2_ppt.py`

## 18장 구성

| # | 슬라이드 | 멘트 |
|---|----------|------|
| 1 | 표지 | Aniverse · 팀 김현우/박서이/김윤주/강유민 · aniverse.my |
| 2 | V1 | 온프레미스 서비스를 EC2 기반 3-tier로 옮긴 첫 번째 구조 |
| 3 | 구성도 V1 | ALB에서 EC2, RDS로 이어지는 서비스 흐름 |
| 4 | V1 한계 / V2에서 바꾼 점 / V2의 핵심 | 제목과 칼럼명 일치 |
| 5 | V2 | EKS에서 배포·복구·관측·인증을 하나의 흐름으로 구성 |
| 6 | 구성도 V2 | Actions→ECR→Argo→EKS · Redis·ESO·OIDC/SSO 뱃지 |
| 7 | V2 상세 ① | DB Pod, 배포 이미지 태그, 재구축 후 데이터 복구 |
| 8 | V2 상세 ② | Zero-Key(OIDC·SSO) · WAF · DNS 유지 · 이관 한 줄 |
| 9 | 검증 기준 | 확인/구성 기준 설명 · Tempo 포함 |
| 10 | 기술 스택 | Argo 아이콘 · Tempo/Grafana/Alert · TF·IRSA·ESO |
| 11 | 데이터 흐름 | PVC vs S3 · 시드(Git SQL) / 주기 백업(S3) 경로 |
| 12 | 앞으로 보완할 점 | 트레이싱은 성과로 이동 · 발표·시연 칸 삭제 |
| 13 | 부하 · 트레이싱 | HPA 2→4 · /works 병목 · Redis Timeout 재검증 |
| 14 | 트러블슈팅 · GitOps·CI/CD | 현우 |
| 15 | 트러블슈팅 · EKS | 서이 |
| 16 | 트러블슈팅 · DB·관측 | 윤주 |
| 17 | V2 일정 | 실제 커밋 날짜에 맞춘 DB·관측·추적 일정 |
| 18 | Q & A | 팀 역할 한 줄 |

## 8장 발표 멘트

파드와 CI는 OIDC로 Access Key가 돌지 않게 막고, 사람은 SSO로 임시 자격증명만 받습니다. 장기 키를 최소화한 Zero-Key가 핵심입니다. 계정 접근이 제한되어 복구가 어려웠을 때 팀원 계정으로 이관하며 이 구조로 전환했습니다. (원인은 확정하지 않음 — 질문 시 “정확한 원인은 확정되지 않았고, 재발 방지로 장기 키 없는 구조로 바꿨다”.)

## 11장 Q&A 대비

주기 백업은 S3에 쌓고, destroy 후 시드 복구는 GitHub의 SQL로 합니다. “S3 백업으로 바로 복구하나요?” → 현재 자동 복구 Job은 Git SQL 경로이고, S3 덤프 복구는 보완 과제입니다.

## 13–16장 발표 멘트

**13장 · 부하테스트·트레이싱** — 부하테스트에서 web 파드가 2개에서 4개로 늘어나는 것을 확인했습니다. `/works/` 응답은 최대 약 2.91초로 가장 느렸고, ASGI 계측 패키지를 보완한 뒤 Tempo에서 실제 요청 트레이스를 확인했습니다. Redis TimeoutError는 의존성 버전을 조정했으며 같은 부하 조건에서 재검증이 남아 있습니다.
**14장 · 현우** — 중지 검증, Argo Missing(SSA), 시드 행 검증  
**15장 · 서이** — HPA replicas 충돌, Terraform 생성 순서, DB 비밀번호 로테이션  
**16장 · 윤주** — 백업 0바이트, Alloy max-pods, Slack 웹훅

## 18장 팀 역할

- 김현우 — GitOps·CI/CD
- 박서이 — EKS·네트워크·보안
- 김윤주 — 컨테이너·DB·관측
- 강유민 — 서비스 UI·콘텐츠

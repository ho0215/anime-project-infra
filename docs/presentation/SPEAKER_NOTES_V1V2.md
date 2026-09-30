# Aniverse V1→V2 발표 대본 (작업 기준본 · 16장)

PPT: `ppt/Aniverse_V1V2_발표_working.pptx`  
내용 문서: `CONTENT_V1V2_working.md`  
생성: `python3 make_hybrid_diagrams.py` → `python3 make_aniverse_v1v2_ppt.py`

## 16장 구성

| # | 슬라이드 | 멘트 |
|---|----------|------|
| 1 | 표지 | Aniverse · 팀 김현우/박서이/김윤주/강유민 · aniverse.my |
| 2 | V1 정의 | ALB→ASG/EC2→RDS · 온프렘→AWS · Terraform+CodeDeploy |
| 3 | 구성도 V1 | VPC 스타일 한 장으로 V1 흐름 |
| 4 | V1 한계·V2 목표·차별 | 관측 / 반영 지연 / ASG 비용 → V2로 대응 |
| 5 | V2 정의 | EKS+GitOps 재현 · 데이터·관측·보안 한 사이클 |
| 6 | 구성도 V2 | EKS · Argo · PVC · S3 |
| 7 | V2 상세 ① | DB Pod · sha 태그 · 시드 복구 |
| 8 | V2 상세 ② | Zero-Key: OIDC는 파드·CI, SSO는 사람. DNS는 destroy 후에도 유지 |
| 9 | 검증 기준 | health·시드·GitOps·미디어·Slack 충족. Tempo는 향후 |
| 10 | 기술 스택 | 6칸 아이콘 맵 (앱~관측) |
| 11 | 데이터 흐름 | PVC vs S3 · 시드/백업/미디어 경로 |
| 12 | 향후 3UP | Unique: 관측·OIDC·백업 + **AIOps(self-healing)** |
| 13 | 트러블슈팅 · 노드 | 현우 30초. stop 성공 ≠ 워커 종료. maxSize는 0 불가. 성공 조건은 인스턴스 0 |
| 14 | 트러블슈팅 · EKS | 서이. HPA replicas 충돌, 빈 계정 생성 순서, 시크릿 값 교체. 각 한 문장 |
| 15 | 트러블슈팅 · DB·관측 | 윤주. 백업 0바이트, Alloy 파드 한도, Slack 웹훅 마운트. 각 한 문장 |
| 16 | V2 일정 | 준비·구축·이관·복구·정리. 9/29 EKS 칸에 RBAC |

## 5~7분 배분

- 1–4: ~2분 (V1·한계·전환 논리)
- 5–8: ~2분 20초 (V2 정의·구성도·상세)
- 9–11: ~1분 40초 (검증·스택·데이터 흐름)
- 12: ~30초 (AIOps·다음)

## 포인트

- **V1** = EC2 3-tier로 먼저 서비스 (온프렘→AWS)
- **V2** = 학습용 DB Pod · Git 태그 일치 · 시드 · OIDC · DNS keep
- Actions 초록 ≠ 시드/목록 검증

## 8장에서 덧붙일 말

파드와 CI는 OIDC, 사람은 SSO입니다. 둘 다 장기 키를 갖지 않는 Zero-Key입니다. DNS는 지워도 남깁니다.

## 13–15장에서 말할 말

13장(현우), 30초. stop은 성공인데 워커가 남아 있었습니다. 개수만 0으로 바꾸고 끝내서 Autoscaler가 다시 띄웠고, EKS는 maxSize 0을 받지 않습니다. Launch를 멈추고 인스턴스가 0대인 것을 성공으로 봤습니다.

14장(서이), 항목마다 한 문장. HPA와 배포 파일이 같은 개수를 같이 고치고 있었습니다. 빈 계정에서 처음부터 만들자 숨은 순서가 드러났습니다. 시크릿을 옮길 때 값까지 난수로 바꿨습니다.

15장(윤주), 항목마다 한 문장. 백업이 0바이트였던 이유는 헤드리스 서비스라 밖에서 접속이 안 된 것입니다. Alloy는 노드 파드 한도 때문에 빠졌습니다. Slack은 웹훅 파일을 파드에 마운트하지 않아서 안 왔고, 마운트 뒤에 수신을 확인했습니다.

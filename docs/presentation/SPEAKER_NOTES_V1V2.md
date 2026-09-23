# Aniverse V1→V2 발표 대본 (작업 기준본 · 10장)

PPT: `ppt/Aniverse_V1V2_발표_working.pptx` (업로드 확정본)  
내용 문서: `CONTENT_V1V2_working.md`  
생성: `python3 make_aniverse_v1v2_ppt.py` (재생성 시 working·vN 갱신)

## 10장 구성

| # | 슬라이드 | 멘트 |
|---|----------|------|
| 1 | 표지 | Aniverse · 팀 김현우/박서이/김윤주/강유민 · aniverse.my |
| 2 | V1 정의 | ALB→ASG/EC2→RDS · 온프렘→AWS · Terraform+CodeDeploy |
| 3 | 구성도 V1 | VPC 스타일 한 장으로 V1 흐름 |
| 4 | V1 한계·V2 목표·차별 | 관측 / 반영 지연 / ASG 비용 → V2로 대응 |
| 5 | V2 정의 | EKS+GitOps 재현 · 데이터·관측·보안 한 사이클 |
| 6 | 구성도 V2 | EKS · Argo · PVC · S3 |
| 7 | V2 강점 | 재현·스케일·DB·OIDC·관측 |
| 8 | 검증 기준 | health·시드·GitOps·미디어 충족 / 관측·알림 예정 |
| 9 | 스택·데이터 흐름 | Django/Helm/EKS · Users→ALB→web→db/PVC |
| 10 | 향후 3UP | Unique: 관측·OIDC·백업 + **AIOps(self-healing)** |

## 5~7분 배분

- 1–4: ~2분 (V1·한계·전환 논리)
- 5–7: ~2분 (V2 정의·구성도·강점)
- 8–9: ~1분 30초 (검증·스택)
- 10: ~30초 (AIOps·다음)

## 포인트

- **V1** = EC2 3-tier로 먼저 서비스 (온프렘→AWS)
- **V2** = 재현·비용·관측을 위해 EKS + Argo + PVC
- 구성도는 각 버전 **정의 직후 1장**
- Actions 초록 ≠ 시드/목록 검증

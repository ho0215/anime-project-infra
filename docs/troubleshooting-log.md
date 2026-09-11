# Aniverse 트러블슈팅 로그

이 문서는 프로젝트 진행 중 발생한 장애·이슈를 기록한다.  
Cursor 에이전트와 함께 해결할 때 항목을 추가한다. (요청: 「로그에 남겨줘」)

| 항목 | 내용 |
|------|------|
| 프로젝트 | Aniverse |
| 관련 계획 | [EKS 전환 계획서](./eks-migration-plan.md) |
| 기록 규칙 | 최신 항목을 **위쪽**에 추가 · 계획 변경 시 `계획 변경`란 작성 |

---

## 템플릿 (복사해서 사용)

```markdown
### YYYY-MM-DD — (짧은 제목)

| 항목 | 내용 |
|------|------|
| 담당 | |
| 환경 | 로컬 / EC2 / minikube / EKS / 기타 |
| 관련 파트 | GitOps · CI/CD / 네트워크 · 컴퓨트 / 컨테이너 · DB |
| 증상 | |
| 가설 | |
| 원인 | |
| 조치 | |
| 재발 방지 | |
| 계획 변경 | 없음 / (있다면 사유) |
| PR · 커밋 | |
| 참고 | |
```

---

## 로그

<!-- 새 항목은 이 선 바로 아래에 추가 -->

### (예시) 2026-08-26 — CodeDeploy ApplicationStop / agent 미기동

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | AWS (ASG · CodeDeploy) |
| 관련 파트 | GitOps · CI/CD / 컴퓨트 |
| 증상 | 배포 실패 `HEALTH_CONSTRAINTS`, ApplicationStop에서 agent가 lifecycle 이벤트를 받지 못함 |
| 가설 | ALLOWED_HOSTS · 헬스체크 경로 문제 |
| 원인 | ALB `/health/`는 먼저 healthy인데, CodeDeploy agent가 Secrets/EFS **이후**에 설치되어 배포 시점에 agent 미기동 |
| 조치 | user_data에서 agent를 부팅 초기에 설치 · deployment group 보정 |
| 재발 방지 | 부팅 순서(헬스 vs agent)를 체크리스트에 포함 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #25 등 |
| 참고 | EC2/CodeDeploy(v1) 사례 — EKS 전환 후에도 “표면 로그 ≠ 원인” 교훈으로 활용 |

---

## 인덱스 (제목만)

| 날짜 | 제목 | 담당 | 환경 |
|------|------|------|------|
| 2026-08-26 | CodeDeploy ApplicationStop / agent 미기동 | 현우 | AWS ASG |

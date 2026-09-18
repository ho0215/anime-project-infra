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

### 2026-09-18 — AWS 계정 Blocked — `iac-admin` Access Key 유출

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | AWS 계정 / GitHub Actions / EKS |
| 관련 파트 | 보안 · 계정 / GitOps · CI/CD |
| 증상 | Actions·콘솔 모두 `StartInstances` → `Blocked`. Support Resolved 후에도 제한 유지 → 전담팀 에스컬레이션 |
| 가설 | GitHub Actions start가 원인? → **아님** (콘솔도 동일) |
| 원인 | **`iac-admin` 장기 Access Key 유출**. AWS가 `AKIAZ4OSWTZ7DVWXNPH2` 도용 지목. CloudTrail **9/17** `iac-admin`이 NAT AMI가 아닌 AMI로 `RunInstances` 다수 호출. 9/16 `github-actions-terraform`은 정상 Terraform. 발표자료「GitHub .env에 iac-admin 키 노출」과 일치 |
| 조치 | 키 삭제·무단 리소스 정리·Support 회신. CI는 **OIDC만** (장기 키 불필요) |
| 재발 방지 | Access Key 금지, `.env`/깃에 키 금지, MFA, Budgets, OIDC Admin 권한 축소(후속) |
| 계획 변경 | 활성화 전까지 EC2/NAT/워커 start 불가 |
| PR · 커밋 | Actions `35291530311` 등 |
| 참고 | 표면은 start 실패, 근본은 **키 유출 → 무단 RunInstances → 계정 Block** |

### 2026-09-16 — EKS stop Actions 성공인데 EC2 워커가 안 꺼짐

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | EKS / GitHub Actions |
| 관련 파트 | 네트워크 · 컴퓨트 / GitOps · CI/CD |
| 증상 | `EKS start/stop` → `stop` 이 Actions **success** 인데 EC2에 워커(+NAT)가 계속 Running |
| 가설 | (1) desired=0 미반영 (2) Cluster Autoscaler 재기동 (3) 비동기 스케일만 호출하고 종료 대기 없음 |
| 원인 | EKS `update-nodegroup-config desired=0` 만 호출 후 즉시 성공 처리. 노드그룹이 `UPDATING` 인 채 끝났고, ASG Desired/인스턴스 수를 검증하지 않음. NAT는 원래 stop 대상이 아니었음 |
| 조치 | stop 시 ASG Launch suspend → EKS desired=0 → **ASG DesiredCapacity=0 직접 설정**(+ scale-in protection 해제) → **인스턴스 0까지 대기** → **NAT `stop-instances`**. start 시 NAT 먼저 기동 후 워커 복구. 워크플로가 ASG empty + NAT stopped 검증 |
| 재발 방지 | stop 성공 조건 = ASG Instances=0 + NAT stopped. Actions만 초록이라고 EC2를 보지 말 것 |
| 계획 변경 | 없음 (당일 stop = 워커+NAT, 컨트롤 플레인은 유지) |
| PR · 커밋 | anime-project-infra #78 |
| 참고 | [eks-start-stop.md](./eks-start-stop.md), Actions run `35074771493` 검증 통과 |

### 2026-09-16 — EKS stop `maxSize=0` API 거절

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | EKS / GitHub Actions |
| 관련 파트 | 네트워크 · 컴퓨트 |
| 증상 | stop 실패: `Invalid value for parameter scalingConfig.maxSize, value: 0, valid min value: 1` |
| 가설 | Autoscaler 재기동 막으려면 max도 0이어야 한다 |
| 원인 | **EKS API는 maxSize 최소 1**. `maxSize=0` 불가 |
| 조치 | `desired=0`, `max=1` + **ASG Launch(등) suspend** 로 Autoscaler/스케일업 차단. start 시 ASG resume |
| 재발 방지 | maxSize=0 시도하지 말 것. Autoscaler 대응은 ASG suspend 또는 CA replicas=0 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #77 |
| 참고 | 직전 #76 이 maxSize=0 을 넣어 회귀 → #77 로 교정 |

### 2026-09-16 — EKS stop 후 Cluster Autoscaler가 워커 재기동

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | EKS |
| 관련 파트 | 네트워크 · 컴퓨트 |
| 증상 | stop 이 desired=0 반영됐는데도 EC2에 워커 2대가 다시/계속 보임 |
| 가설 | Autoscaler가 pending Pod(CoreDNS 등)를 보고 노드를 올림 |
| 원인 | stop 이 `min=0, max=4, desired=0` 이라 **max 여유가 남은 채** CA가 SetDesiredCapacity 가능 |
| 조치 | ASG Launch suspend (#77) + 이후 ASG 직접 0 (#78). (maxSize=0 시도는 API 거절로 폐기) |
| 재발 방지 | desired=0 만으로 끝내지 말고 Launch suspend + ASG 강제 0 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #76(시도) → #77·#78(유효 수정) |
| 참고 | EC2에 NAT 1 + 워커 2 = 3대 보인 상황과 연관 |

### 2026-09-16 — EKS start/stop Variables 미설정으로 즉시 실패

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | GitHub Actions |
| 관련 파트 | GitOps · CI/CD |
| 증상 | `Set Variables EKS_CLUSTER_NAME and EKS_NODEGROUP_NAME` 로 stop 실패. OIDC는 성공 |
| 가설 | 레포 Variables 누락 |
| 원인 | 워크플로가 Variables를 **필수**로 검사. 로컬 스크립트는 이미 `aniverse-eks` / `aniverse-nodes` 기본값이 있는데 CI만 막음 |
| 조치 | 워크플로 env 기본값 = Terraform·스크립트와 동일. Variables 있으면 override |
| 재발 방지 | 문서에 Variables 선택 사항으로 명시. 새 워크플로는 스크립트 기본값과 맞출 것 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #75 |
| 참고 | Actions run `35072822647` |

### 2026-09-16 — db-restore Job: `mysqladmin` 없음 / mariadb-admin

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | EKS (Helm Job) |
| 관련 파트 | 컨테이너 · DB / GitOps |
| 증상 | DB restore Job 실패. DB ready 체크 명령 없음 |
| 가설 | MariaDB 이미지에 mysql 클라이언트 도구명이 다름 |
| 원인 | MariaDB 11 이미지에 **`mysqladmin` 없음**. `mariadb-admin` 사용 |
| 조치 | Job 스크립트를 `mariadb-admin` 으로 변경. curl 은 restore 필요할 때만 apt |
| 재발 방지 | MariaDB 이미지 기준으로 클라이언트 바이너리 확인할 것. CI verify 워크플로 유지 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project #44 ( #43 미머지 후 재시도 ), infra verify #73 |
| 참고 | [db-restore.md](https://github.com/ho0215/anime-project/blob/main/docs/db-restore.md) |

### 2026-09-16 — db-restore: Argo Sync hook hang / ConfigMap 한도

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | EKS / Argo CD |
| 관련 파트 | GitOps · CI/CD / 컨테이너 · DB |
| 증상 | SQL 자동 복구 Job이 Argo sync에 묶여 멈추거나, 덤프를 ConfigMap으로 넣다 실패 |
| 가설 | hook 대기·리소스 크기 제한 |
| 원인 | (1) Sync hook Job이 operation을 붙잡음 (2) ConfigMap/annotation **256Ki** 한도 — SQL 덤프가 큼 |
| 조치 | Sync hook 제거 → 일반 Job. 덤프는 GitHub **raw URL + curl**. stuck op 는 CI에서 terminate. verify는 helm로 Job 직접 apply |
| 재발 방지 | 큰 바이너리/SQL은 ConfigMap에 넣지 말 것. Argo hook은 신중히 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project #42, infra #72·#73 |
| 참고 | values-eks `dbRestore.enabled` |

### 2026-09-16 — S3 wipe verify CI race (sync와 동시 실행)

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | GitHub Actions / S3 |
| 관련 파트 | GitOps · CI/CD |
| 증상 | wipe → restore 검증이 실패하거나, wipe 직후 객체가 다시 200 |
| 가설 | 다른 워크플로가 같은 버킷에 sync |
| 원인 | **Sync media → S3** 와 wipe verify가 동시 실행되어 wipe 직후 재업로드 |
| 조치 | concurrency group `s3-static-assets` 로 직렬화 |
| 재발 방지 | 동일 버킷을 만지는 워크플로는 같은 concurrency group |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #70 |
| 참고 | destroy 후 media 복구 경로와 동일 버킷 |

### 2026-09-16 — DB 복구 후 사진(media) 안 보임

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | EKS / S3 |
| 관련 파트 | 컨테이너 · DB / 스토리지 |
| 증상 | SQL restore 후 HTML은 뜨는데 goods/works 이미지가 깨짐(403/미존재) |
| 가설 | DB에 경로만 있고 S3 객체가 없음 |
| 원인 | 덤프는 **경로만** 저장. S3 버킷은 destroy/`force_destroy` 시 객체 삭제. SQL ≠ 미디어 파일 |
| 조치 | infra **Sync media → S3** / `restore-s3-assets.sh`. Terraform CD apply 후 restore job 연동. 문서화 |
| 재발 방지 | destroy→apply 체크리스트에 DB Job + S3 sync 둘 다 포함 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #69·#70, anime-project #40 |
| 참고 | [static-s3.md](https://github.com/ho0215/anime-project/blob/main/docs/static-s3.md), [eks-start-stop.md](./eks-start-stop.md) |

### 2026-09-16 — Helm `--set-string` 쉼표로 ALLOWED_HOSTS 깨짐

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | Helm / EKS |
| 관련 파트 | 컨테이너 · GitOps |
| 증상 | `DJANGO_ALLOWED_HOSTS` 등 다중 호스트가 잘못 파싱됨 |
| 가설 | 셸/Helm 이스케이프 문제 |
| 원인 | Helm `--set` / `--set-string` 이 **쉼표를 구분자**로 씀 |
| 조치 | 쉼표 있는 값은 **values 파일에만** 기록. 문서·스크립트에서 `--set-string` 사용 금지 |
| 재발 방지 | values-eks.yaml 주석에 명시 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project #36 |
| 참고 | Gabia DNS 안내도 같이 정리 |

### 2026-09-16 — `/health/` DisallowedHost (probe Host)

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | EKS |
| 관련 파트 | 컨테이너 · 네트워크 |
| 증상 | readiness/liveness 실패, Django `DisallowedHost` |
| 가설 | ALLOWED_HOSTS에 ALB 호스트만 있음 |
| 원인 | probe가 기본 Host(파드 IP 등)로 요청 → Django가 거부 |
| 조치 | probe에 `Host: aniverse.my` 헤더. ALLOWED_HOSTS에 와일드카드/`*` 보강(values-eks) |
| 재발 방지 | Django + K8s probe 조합 시 Host 헤더 필수 검토 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project #35 |
| 참고 | Ingress ACM HTTPS 와 함께 정리(#39) |

### 2026-09-16 — ECR `AlreadyExists` (state에 없음)

| 항목 | 내용 |
|------|------|
| 담당 | 현우 |
| 환경 | Terraform / ECR |
| 관련 파트 | GitOps · CI/CD |
| 증상 | apply 시 ECR 리포지토리 AlreadyExists |
| 가설 | 콘솔/이전에 만든 리포가 state 밖 |
| 원인 | 실존 리소스와 Terraform state 불일치 |
| 조치 | state **import** |
| 재발 방지 | 수동 생성 리소스는 import 또는 data source. EKS-only 정리 시 주의 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #60 |
| 참고 | D-007 EKS-only 리팩터와 같은 날 |

### 2026-09-16 — kubectl 클러스터 권한 없음 (Access Entry)

| 항목 | 내용 |
|------|------|
| 담당 | 서이 / 현우 |
| 환경 | EKS |
| 관련 파트 | 네트워크 · 컴퓨트 |
| 증상 | 로컬 `kubectl` 권한 거부 |
| 가설 | aws-auth / Access Entry 미등록 |
| 원인 | EKS API 인증 모드에서 **Access Entry** 누락 |
| 조치 | 부여 스크립트 + Terraform에 iac-admin Access Entry 고정 |
| 재발 방지 | 클러스터 생성자 외 IAM은 Access Entry를 코드로 관리 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #61·#62 |
| 참고 | — |

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
| 2026-09-18 | AWS 계정 Blocked — iac-admin Access Key 유출 | 현우 | AWS / Actions |
| 2026-09-16 | EKS stop Actions 성공인데 EC2 워커가 안 꺼짐 | 현우 | EKS / Actions |
| 2026-09-16 | EKS stop `maxSize=0` API 거절 | 현우 | EKS / Actions |
| 2026-09-16 | EKS stop 후 Cluster Autoscaler가 워커 재기동 | 현우 | EKS |
| 2026-09-16 | EKS start/stop Variables 미설정으로 즉시 실패 | 현우 | Actions |
| 2026-09-16 | db-restore Job: mysqladmin 없음 / mariadb-admin | 현우 | EKS Helm |
| 2026-09-16 | db-restore: Argo Sync hook hang / ConfigMap 한도 | 현우 | Argo / EKS |
| 2026-09-16 | S3 wipe verify CI race | 현우 | Actions / S3 |
| 2026-09-16 | DB 복구 후 사진(media) 안 보임 | 현우 | EKS / S3 |
| 2026-09-16 | Helm `--set-string` 쉼표로 ALLOWED_HOSTS 깨짐 | 현우 | Helm |
| 2026-09-16 | `/health/` DisallowedHost (probe Host) | 현우 | EKS |
| 2026-09-16 | ECR AlreadyExists (state에 없음) | 현우 | Terraform |
| 2026-09-16 | kubectl 클러스터 권한 없음 (Access Entry) | 서이/현우 | EKS |
| 2026-08-26 | CodeDeploy ApplicationStop / agent 미기동 | 현우 | AWS ASG |

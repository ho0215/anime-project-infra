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

### 2026-09-23 — db-restore Actions 초록인데 시드 데이터 없음 (migrate Skip)

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | EKS / Actions (신계정 841535407395) |
| 관련 파트 | 컨테이너 · DB / GitOps · CI/CD |
| 증상 | 사이트 `/deal/`·`/works/` 「등록된 … 없습니다」. [Verify DB restore #35804566982](https://github.com/ho0215/anime-project-infra/actions/runs/35804566982) 는 **success** (54s) |
| 가설 | 덤프 경로 잘못 · Job 미실행 · raw URL 404 |
| 원인 | Job 로그 `table_count=25 (min=20)` → **`Skip restore — schema already present.`** 웹 Pod `migrate`가 빈 테이블만 먼저 생성. Job은 테이블 수만 보고 exit 0. Kubernetes Job은 Complete 후 덤프 갱신만으로 **재실행되지 않음**. (덤프·raw URL·`dbRestore.enabled`는 정상) |
| 조치 | Skip 조건을「테이블 ≥ min **그리고** `anime_anime` 행 > 0」으로 변경. 시드 0이면 force SQL import (`DROP TABLE IF EXISTS` 덤프). Verify는 Skip-only 성공을 시드 검증으로 보강, `APP_REF` stale 브랜치 → `main`/`app_ref` input |
| 재발 방지 | Verify step summary/로그에 `Restore complete`·`seed_rows` 필수. 「Actions 초록 ≠ 데이터 복구」. DB만 비면 **Verify DB restore**만; Argo CD on EKS는 ALB/HTTPS/전체용. EC2 SSH 복구 경로 없음(EKS Pod+PVC). 런북: anime [db-restore.md](https://github.com/ho0215/anime-project/blob/main/docs/db-restore.md) |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project #55, anime-project-infra #100 |
| 참고 | Job Complete 16h·5s 실행 → Skip 전형. media는 SQL과 별도 → Sync media → S3 |

### 2026-09-23 — OutOfSync만으로 「사이트 다운」으로 오인 / image.tag drift

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | EKS / Argo CD / Docker build |
| 관련 파트 | GitOps · CI/CD |
| 증상 | Argo `OutOfSync` + (가끔) install wait 실패/경고. HTTPS·health는 200 |
| 가설 | sync 실패 = 장애 |
| 원인 | Docker build가 Helm `image.tag` 만 Git bump하고 Argo sync가 안 따라가면 Deployment drift → OutOfSync. Missing=0·Healthy면 페이지는 살아 있음 |
| 조치 | docker-build에 bump 직후 Argo apply sync (`continue-on-error`). argocd-eks-install wait는 Healthy/Progressing+Missing=0이면 OutOfSync여도 OK |
| 재발 방지 | OutOfSync ≠ Missing. Missing/ComparisonError만 차단으로 볼 것 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project #54 |
| 참고 | ECR/OIDC 역할에 EKS 없으면 sync step warning 후 skip — infra 역할·Access Entry 필요 시 별도 |

### 2026-09-23 — Bind domain: helm upgrade가 빈 secrets로 Secret 덮어씀

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | EKS / Actions (Argo CD on EKS → Bind domain) |
| 관련 파트 | GitOps · CI/CD / 컨테이너 |
| 증상 | Bind/helm upgrade 실패 또는 앱 Secret이 깨짐. `secrets.DJANGO_SECRET_KEY required` |
| 가설 | values에 secrets 없음 · Argo parameters만 있음 |
| 원인 | `eks-bind-domain`/helm upgrade가 **live Secret을 `--set-string`으로 안 주입**한 채 chart 기본(빈 값)으로 upgrade → Secret 덮어쓰기 또는 required 에러 |
| 조치 | live `aniverse-app-secrets` 를 읽어 helm에 주입. Argo seed secrets 스텝과 정합 |
| 재발 방지 | helm upgrade 경로마다 live secret 주입 필수. Secret 없는 adopt/bind 금지 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project #53, infra seed #94 |
| 참고 | 신계정 이관 직후 Bind 단계에서 재발 |

### 2026-09-23 — `cancelled()`를 run 스크립트에 넣으면 workflow startup_failure

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | GitHub Actions (Argo CD on EKS) |
| 관련 파트 | GitOps · CI/CD |
| 증상 | 워크플로가 본문 실행 전에 **startup_failure** (1s). Cancel이 안 먹는 것과 별개로 “취소 개선” 커밋 후 즉시 실패 |
| 가설 | concurrency/cancel 설정 문제 |
| 원인 | GitHub Actions **`cancelled()` 는 `if:` 컨텍스트 전용**. `run: \|` 셸 안에서 쓰면 표현식 평가 단계에서 워크플로가 기동 실패 |
| 조치 | `cancelled()` 를 run 본문에서 제거. 취소를 쓰려면 `if: ${{ !cancelled() }}` 등 **step if** 만 사용 |
| 재발 방지 | Actions 문서: 함수는 if/환경 제한 문맥만. 셸에 넣지 말 것 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #99 |
| 참고 | #96 concurrency cancel 과 구분해서 볼 것 |

### 2026-09-22 — ACM PENDING인데 HTTPS Ingress → ALB ADDRESS 영구 없음

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | EKS / ACM / ALB |
| 관련 파트 | 네트워크 · 컴퓨트 / GitOps |
| 증상 | Ingress에 ALB hostname(ADDRESS) 안 생김. HTTPS 복구·Wait Ingress 실패 |
| 가설 | subnet tag · LB Controller · security group |
| 원인 | 인증서 **PENDING_VALIDATION** 인데 Ingress에 `certificate-arn` HTTPS 어노테이션 적용 → ALB Controller가 리스너/ADDRESS를 못 만듦 |
| 조치 | Argo/HTTPS 복구 전 **ACM ISSUED** 게이트 (DNS validation upsert + wait). ISSUED 후에야 HTTPS Ingress. values에 주석 |
| 재발 방지 | ACM 상태 확인 없이 HTTPS 어노테이션 넣지 말 것. PENDING=ALB 없음으로 먼저 의 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #98, anime-project #51·#46 |
| 참고 | 계정 이관 후 새 ACM이 PENDING인 동안 반복 실패 |

### 2026-09-22 — Argo Missing: Job sync-wave가 Ingress Progressing에 막힘

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | EKS / Argo CD |
| 관련 파트 | GitOps / 컨테이너 · DB |
| 증상 | Application health=`Missing`. `aniverse-db-restore` Job이 클러스터에 안 보이거나 영구 Missing |
| 가설 | SSA · Job 실패 · helm 미적용 |
| 원인 | Job에 **sync-wave(예: 5)** 를 두면, Argo는 이전 wave가 Healthy일 때만 다음 wave 적용. Ingress(ALB)는 ADDRESS 전까지 **Progressing** → Job wave가 영구 차단 |
| 조치 | Job에서 높은 sync-wave 제거(DB ready는 Job 내부 `mariadb-admin ping`). Ingress ignore-healthcheck 등 보조 |
| 재발 방지 | ALB 의존 리소스보다 **뒤 wave에 Job 두지 말 것**. Missing이면 wave/Ingress health부터 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project #50 |
| 참고 | SSA Missing(#49·#97)과 증상이 비슷해 원인 혼동하기 쉬움 |

### 2026-09-22 — ComparisonError `terminatingReplicas` / live ServerSideApply 잔존

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | EKS / Argo CD |
| 관련 파트 | GitOps |
| 증상 | Application `ComparisonError`, health=`Missing` 또는 sync 불가. 리소스는 있는데 Argo가 비교 실패 |
| 가설 | CRD/스키마 · OutOfSync |
| 원인 | syncOptions에 **ServerSideApply** 쓰면 Deployment 등에서 `terminatingReplicas` 필드 비교 오류. live Application에 SSA가 남아 sanitize 후에도 재발 |
| 조치 | SSA 제거, client-side apply sync. install 후 syncOptions를 `CreateNamespace`+`RespectIgnoreDifferences`로 **강제 replace**. strip SSA CI 스텝 |
| 재발 방지 | 이 차트/버전 조합에서 SSA 기본 사용 금지. Missing이면 `syncOptions`에 ServerSideApply 있는지 먼저 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project #48·#49, infra #97 |
| 참고 | sync-wave Missing(#50)과 병행 디버깅했음 |

### 2026-09-22 — Missing 대기 ~8분 → 짧게 끊고 helm fallback

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | Actions / argocd-eks-install |
| 관련 파트 | GitOps · CI/CD |
| 증상 | Argo CD on EKS가 Missing에서 수 분~십수 분 대기. Cancel도 잘 안 먹힘 |
| 원인 | wait 루프가 Synced만 고집하고 Missing을 오래 재시도 |
| 조치 | `ARGO_SYNC_MAX_WAIT`·`EARLY_MISSING`(연속 Missing N회면 즉시 중단) 후 helm fallback/진단 덤프 |
| 재발 방지 | Missing은 “기다리면 낫는” 상태가 아님. 짧게 실패·덤프 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project #52, infra wait env |
| 참고 | #96 cancel-in-progress 와 함께 체감 개선 |

### 2026-09-22 — Argo 워크플로 재실행 시 이전 런이 안 죽음 (`cancel-in-progress: false`)

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | GitHub Actions |
| 관련 파트 | GitOps · CI/CD |
| 증상 | Actions Cancel / 재실행해도 이전 Argo 설치 잡이 계속 돌거나 큐만 쌓임 |
| 원인 | concurrency `cancel-in-progress: **false**` |
| 조치 | 해당 워크플로 그룹에서 재실행 시 이전 런 취소하도록 변경 (`true`) |
| 재발 방지 | 장시간 wait 워크플로는 cancel-in-progress 기본 검토. UI Cancel ≠ concurrency 설정 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #96 |
| 참고 | #99 `cancelled()` 오용 startup_failure 와 별개 |

### 2026-09-22 — Helm adopt / ALB 대기 ownership 충돌

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | EKS / Helm / Argo |
| 관련 파트 | GitOps · 네트워크 |
| 증상 | helm upgrade 실패(리소스 already exists / ownership). ALB 대기와 복구 순서 꼬임 |
| 원인 | Argo가 만든 리소스를 Helm이 소유권 없이 adopt하려다 충돌. ALB 생성 전 bind |
| 조치 | Helm adopt 옵션·레이블/annotation 정리 + ALB ADDRESS 대기 후 bind. Restore ALB HTTPS 워크플로와 정렬 |
| 재발 방지 | Argo 관리 리소스에 무보정 helm upgrade 금지. adopt 명시 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #95·#93 |
| 참고 | secrets 시드(#94) 이후 단계 |

### 2026-09-22 — 앱 Secret 없이 Argo/Helm 복구 시작

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | EKS (신계정 apply 직후) |
| 관련 파트 | GitOps · CI/CD |
| 증상 | chart `secrets.* required` 로 sync/helm 실패. 빈 클러스터에 Application만 적용 |
| 원인 | Argo helm.parameters / K8s Secret 시드 전에 sync |
| 조치 | Argo CD on EKS에 **Seed aniverse-app-secrets** 스텝 후 install/sync |
| 재발 방지 | 신규 계정·namespace 재생성 시 secrets 시드가 선행 체크리스트 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #94 |
| 참고 | #53 bind live secrets 와 쌍 |

### 2026-09-22 — kubernetes/helm provider 15분 토큰 만료 → Unauthorized

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | Terraform (EKS kubernetes/helm provider) |
| 관련 파트 | GitOps · CI/CD |
| 증상 | apply 중반 `Unauthorized` / exec 인증 실패 |
| 원인 | EKS 토큰(~15분)을 provider가 재발급하지 않음 |
| 조치 | exec 인증으로 토큰 갱신되게 provider 설정 |
| 재발 방지 | 장시간 apply는 exec auth. 정적 kubeconfig 토큰 금지 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #90 |
| 참고 | 계정 이관 직후 장시간 apply에서 노출 |

### 2026-09-22 — NAT·프라이빗 RT 전에 노드그룹 생성

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | Terraform EKS |
| 관련 파트 | 네트워크 · 컴퓨트 |
| 증상 | 노드 NotReady / 이미지 pull·egress 실패. 노드그룹 생성은 됐지만 프라이빗 경로 없음 |
| 원인 | NAT·프라이빗 라우트 완료 전 노드그룹 의존성 부족 |
| 조치 | NAT·RT 완료 후 노드그룹. NAT AMI SSM |
| 재발 방지 | module depends_on / 순서 문서화. start 시에도 NAT 먼저(#78) |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #89 |
| 참고 | stop/start NAT 이슈(#78)와 동일 계열 |

### 2026-09-22 — 계정 이관(6795…→8415…) 후 ECR/ACM/values 불일치

| 항목 | 내용 |
|------|------|
| 담당 | Cursor / 팀 |
| 환경 | AWS 신계정 841535407395 |
| 관련 파트 | 전체 (ECR · ACM · Route53 · EKS) |
| 증상 | 이미지 pull 실패(구 ECR), HTTPS/ALB 안 됨(구 ACM ARN), Actions OIDC 역할 불일치 |
| 원인 | 계정 이전 후 리소스 ARN·레지스트리·인증서가 새 계정 것인데 Git values/CI vars가 구계정 잔존 |
| 조치 | values-eks ECR·ACM 신계정으로 복구(#46). Terraform CI Access Entry(#92). OIDC 역할 신계정. migration PR #88 |
| 재발 방지 | 계정 이관 체크리스트: ECR URL, ACM ARN, Route53, OIDC trust, Access Entry, S3 버킷명 |
| 계획 변경 | 운영 계정 = 841535407395 |
| PR · 커밋 | infra #88·#92, anime #46 |
| 참고 | 이후 ACM PENDING(#98)·secrets(#94)·Missing 연쇄의 배경 |

### 2026-09-22 — Terraform CD: state에 있는데도 Access Entry/NAT IAM import 재시도

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | Terraform CD |
| 관련 파트 | GitOps · CI/CD |
| 증상 | import 단계 실패 또는 불필요 재import |
| 원인 | state에 리소스가 있어도 import 스크립트가 무조건 시도 |
| 조치 | state에 있으면 import 스킵 |
| 재발 방지 | import 헬퍼에 `terraform state list` 가드 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #91 |
| 참고 | 계정 이관·재apply 시 |

### 2026-09-22 — Terraform CI 역할에 EKS ClusterAdmin 없음

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | EKS / Actions |
| 관련 파트 | GitOps · CI/CD |
| 증상 | CI `kubectl`/`helm` Unauthorized 또는 forbidden |
| 원인 | `aniverse-github-actions-terraform` 등에 Access Entry(ClusterAdmin) 미부여 |
| 조치 | Terraform으로 CI 역할 Access Entry 고정 |
| 재발 방지 | 클러스터 재생성 후 Access Entry를 코드로 재적용 (#61·#62 iac-admin과 동일 패턴) |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #92 |
| 참고 | 로컬 kubectl 권한 이슈(2026-09-16)의 CI 버전 |

### 2026-08-26 — ALB HTTPS 뒤 Nginx가 X-Forwarded-Proto 미보존

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | EKS / Nginx sidecar (또는 컨테이너 Nginx) |
| 관련 파트 | 네트워크 / 컨테이너 |
| 증상 | HTTPS로 들어오는데 리다이렉트 루프·혼합 콘텐츠·Django `is_secure()` false |
| 원인 | ALB가 종료한 TLS 뒤 앱/Nginx가 `X-Forwarded-Proto` 를 신뢰·전달하지 않음 |
| 조치 | Nginx에서 `X-Forwarded-Proto` 보존·전달, 로컬 health는 예외 |
| 재발 방지 | USE_HTTPS=True + ALB 구성 시 프록시 헤더 체크리스트 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project (nginx-https-forwarded-proto) |
| 참고 | ACM/ALB 복구와 함께 볼 것 |

### 2026-08-25 — S3 static 버킷 destroy 시 BucketNotEmpty

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | Terraform destroy |
| 관련 파트 | 스토리지 |
| 증상 | static S3 버킷 삭제 실패 `BucketNotEmpty` |
| 원인 | 객체 남은 버킷은 기본으로 destroy 불가 |
| 조치 | `force_destroy` (또는 사전 비우기) 로 destroy 가능하게 |
| 재발 방지 | lab/dev 버킷은 force_destroy 명시. 운영은 정책 합의 |
| 계획 변경 | 없음 |
| PR · 커밋 | anime-project-infra #17 |
| 참고 | media wipe→restore 검증(#70)과 계열 |

### 2026-09-18 — destroy 재실행이 state lock 으로 즉시 실패

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | Terraform CD destroy |
| 증상 | [run 35325490995](https://github.com/ho0215/anime-project-infra/actions/runs/35325490995) `Error acquiring the state lock` (S3 use_lockfile PreconditionFailed). Lock ID `887a3d59-…`, Who `runner@…`, Created 이전 취소된 destroy 재시도 시각 |
| 원인 | VPC DependencyViolation 중이던 run 을 Cancel 하면 S3 lockfile 이 남음. ENI 는 이미 없음 (`VPC has no ENIs`) — 이번 실패는 VPC가 아니라 **락** |
| 조치 | destroy 에 `-lock-timeout` + runner 스테일 락 `force-unlock` 후 재시도. VPC delete timeout 45m·ENI permission 정리도 포함 |
| PR · 커밋 | `cursor/vpc-timeout-eni-8e41` |

### 2026-09-18 — VPC destroy 가 10분+ Still destroying

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | Terraform CD destroy |
| 증상 | `module.network.aws_vpc.main: Still destroying...` 14분+ |
| 원인 | EKS 삭제 직후 Hyperplane/ENI·SG 가 VPC 에 비동기 잔존. 빈 VPC 면 초 단위지만 EKS 직후엔 정상적으로 수~수십 분 걸리거나 DependencyViolation |
| 조치 | preflight 에 ENI 대기/삭제·VPC endpoint·non-default SG 정리 강화 (재시도 시 효과) |
| PR · 커밋 | `cursor/vpc-eni-cleanup-8e41` |

### 2026-09-18 — 노드그룹 DELETE_FAILED: ReplaceUnhealthy suspend + premature state rm

| 항목 | 내용 |
|------|------|
| 담당 | Cursor |
| 환경 | EKS / Terraform CD destroy |
| 증상 | health: `AutoScalingGroupInvalidConfiguration` (ReplaceUnhealthy suspended). 클러스터 삭제 `ResourceInUseException: nodegroups attached`. 노드 IAM 롤이 노드그룹보다 먼저 Destruction complete |
| 원인 | preflight 가 ReplaceUnhealthy 를 suspend → EKS 가 노드그룹 삭제 거부. DELETE_FAILED 인데 state rm → TF 가 노드 롤 삭제 → AccessDenied 고착 |
| 조치 | delete 전 ASG **resume**(ReplaceUnhealthy). CFN은 ASG physical id 로 스택 조회 후 FORCE. 노드그룹 AWS 삭제 완료 전에는 state rm 거부 |
| PR · 커밋 | `cursor/ng-resume-cfn-8e41` |

### 2026-09-18 — Terraform destroy 실패 (노드그룹 DELETE_FAILED + subnet/IGW DependencyViolation)

| 항목 | 내용 |
|------|------|
| 담당 | 현우 / Cursor |
| 환경 | EKS / GitHub Actions Terraform CD |
| 관련 파트 | 네트워크 · 컴퓨트 / GitOps · CI/CD |
| 증상 | [run 35318377695](https://github.com/ho0215/anime-project-infra/actions/runs/35318377695) destroy 실패. `aniverse-nodes`=`DELETE_FAILED` (AccessDenied / aws-auth), public subnet·IGW `DependencyViolation` (`mapped public address(es)`) |
| 가설 | (1) 계정 Block (2) NAT EIP (3) Ingress ALB 잔여 ENI (4) API 인증 모드에서 노드 Access Entry 부재 |
| 원인 | `authentication_mode=API` 인데 노드 `EC2_LINUX` Access Entry 를 TF 미관리 → 노드그룹 삭제 시 drain 권한 없음. Ingress ALB(`k8s-aniverse-…`)는 TF state 밖이라 LB Controller helm 삭제 후에도 퍼블릭 IP/ENI 잔존 → 서브넷·IGW 삭제 차단 |
| 조치 | … + **ASG 강제 0/terminate + CFN `FORCE_DELETE_STACK`** (Access Entry 재시도만으로 DELETE_FAILED 루프 방지) |
| 재발 방지 | destroy CD 가 preflight 필수. DELETE_FAILED 시 Access Entry 재시도만 하지 말고 ASG/CFN force. S3 ARN으로 count 금지 |
| 계획 변경 | 없음 |
| PR · 커밋 | `cursor/fix-destroy-deps-8e41` |
| 참고 | [terraform-destroy-preflight.sh](../scripts/terraform-destroy-preflight.sh) |

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
| 2026-09-23 | db-restore Actions 초록인데 시드 데이터 없음 (migrate Skip) | Cursor | EKS / Actions |
| 2026-09-23 | OutOfSync만으로 사이트 다운 오인 / image.tag drift | Cursor | Argo / Docker build |
| 2026-09-23 | Bind domain: helm이 빈 secrets로 Secret 덮어씀 | Cursor | EKS / Actions |
| 2026-09-23 | cancelled()를 run에 넣으면 startup_failure | Cursor | Actions |
| 2026-09-22 | ACM PENDING인데 HTTPS Ingress → ALB ADDRESS 없음 | Cursor | ACM / ALB |
| 2026-09-22 | Argo Missing: Job sync-wave가 Ingress Progressing에 막힘 | Cursor | Argo / EKS |
| 2026-09-22 | ComparisonError terminatingReplicas / SSA 잔존 | Cursor | Argo |
| 2026-09-22 | Missing 대기 과다 → 짧게 끊고 helm fallback | Cursor | Actions |
| 2026-09-22 | cancel-in-progress:false 로 이전 런 안 죽음 | Cursor | Actions |
| 2026-09-22 | Helm adopt / ALB ownership 충돌 | Cursor | Helm / Argo |
| 2026-09-22 | 앱 Secret 없이 Argo/Helm 복구 시작 | Cursor | EKS |
| 2026-09-22 | kubernetes/helm 15분 토큰 만료 Unauthorized | Cursor | Terraform |
| 2026-09-22 | NAT·프라이빗 RT 전에 노드그룹 생성 | Cursor | EKS / NAT |
| 2026-09-22 | 계정 이관 후 ECR/ACM/values 불일치 | Cursor | AWS 계정 |
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

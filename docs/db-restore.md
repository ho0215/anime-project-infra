# DB SQL 복구 런북 (EKS)

> 트러블슈팅·장애 기록의 **단일 위치**는 [troubleshooting-log.md](./troubleshooting-log.md).  
> 앱 레포 `docs/db-restore.md` 는 여기로 안내만 한다.

EKS MariaDB는 PVC라 **Terraform destroy 시 데이터가 사라집니다.**  
스키마·시드는 anime-project Git SQL 덤프, 사진은 S3 sync.

## 덤프 위치

| 항목 | 값 |
|------|-----|
| 앱 레포 경로 | `ho0215/anime-project` → `data/aniverse_backup.sql` (**main**) |
| Job URL | Helm `dbRestore.sqlUrl` → `https://raw.githubusercontent.com/ho0215/anime-project/main/data/aniverse_backup.sql` |
| values | anime-project `deploy/helm/aniverse/values-eks.yaml` → `dbRestore.enabled: true` |

로컬 Ubuntu / 예전 앱 EC2에 파일을 두는 경로가 **아님**. main raw URL만 Job이 curl.

## 자동 경로

1. Argo sync 시 Job `aniverse-db-restore` (일반 Job, Sync hook 아님)
2. GitHub raw에서 덤프 curl (ConfigMap 금지 — 256Ki)
3. Skip / Import:
   - 테이블 ≥ `minTables`(20) **그리고** `anime_anime` 행 > 0 → Skip
   - 그 외 (빈 DB · migrate-only 빈 스키마) → SQL import (`DROP TABLE IF EXISTS`)

```bash
kubectl -n aniverse get job aniverse-db-restore
kubectl -n aniverse logs job/aniverse-db-restore -c restore
```

| 로그 | 의미 |
|------|------|
| `Restore complete. … seed_rows=N` (N≥1) | 복구됨 |
| `Skip restore — schema + seed already present.` | 시드 있음 → OK |
| `Skip restore — schema already present.` (구버전) | 테이블만 보고 Skip → **시드 미복구** (anime #55 이전) |

## 무엇을 돌리나

| 목적 | 이 레포 Actions | 비고 |
|------|-----------------|------|
| **DB 시드만** | **Verify DB restore Job** | Job 삭제→helm 재적용. `app_ref` 기본 `main` |
| 클러스터/ALB/HTTPS | **Argo CD on EKS** | DB만이면 필수 아님 |
| 이미지·상품 파일 | **Sync media → S3** | SQL ≠ media |

## destroy 후 복구 순서

1. Terraform apply  
2. Argo CD on EKS (또는 Argo sync)  
3. **Verify DB restore** — `Restore complete` + `seed_rows≥1`  
4. Sync media → S3  
5. `https://aniverse.my/health/` · `/deal/` · `/works/` 목록 확인  

상세 start/stop·DNS: [eks-start-stop.md](./eks-start-stop.md)

## 트러블슈팅 (요약)

자세한 표·PR·날짜별 기록 → **[troubleshooting-log.md](./troubleshooting-log.md)** (2026-09-16 db-restore · 2026-09-23 Skip-초록 등).

| 증상 | 원인 | 조치 |
|------|------|------|
| Actions 초록인데 장터/창작 비어 있음 | migrate 빈 스키마 → Job Skip (exit 0) | Verify 로그에 `seed_rows`. Job 삭제 후 재실행. Complete Job은 자동 재실행 안 됨 |
| 레포에 백업 넣었는데 반영 안 됨 | main 미머지 · Job Complete · Skip | main 머지 + Verify |
| EC2 SSH로 mysql? | 앱 EC2 없음. DB=Pod+PVC | Actions OIDC 또는 Access Entry + kubectl |
| Job Missing / Argo 멈춤 | sync-wave가 Ingress Progressing에 막힘 · SSA | troubleshooting 2026-09-22 Missing/SSA |
| SQL OK · 이미지 깨짐 | media는 S3 | Sync media → S3 |
| Verify가 옛 chart | stale `APP_REF` | `app_ref=main` (#100) |

## 덤프 갱신

앱 레포에서 mysqldump → `data/aniverse_backup.sql` **main 머지** → Verify(또는 Job 재생성).

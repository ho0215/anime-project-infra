# PPT용 — 계정 Block · 계정 이관 트러블슈팅

발표 슬라이드에 옮기기 쉬운 요약본.  
원본 상세: [troubleshooting-log.md](../troubleshooting-log.md)

**스토리 한 줄:** 키 유출로 구계정 Block → 신계정으로 이관 → ARN/인증서/시크릿/Argo 설정이 연쇄로 깨짐 → 하나씩 원인 고정.

| | 구계정 | 신계정 |
|--|--------|--------|
| Account | `679583587966` | `841535407395` |
| 계기 | `iac-admin` Access Key 유출 → Block | 운영 이전 |

---

## 슬라이드 A — 계정 Block (보안)

### 제목
표면은 `EKS start` 실패, 근본은 **Access Key 유출**

### 증상 (1줄)
Actions·콘솔 모두 `StartInstances` → **`Blocked`**

### 잘못된 첫인상
「GitHub Actions / start 스크립트 버그」

### 실제 원인
- `iac-admin` **장기 Access Key**가 GitHub `.env` 등에 노출
- 도용 계정으로 **무단 `RunInstances`** (NAT AMI가 아닌 AMI)
- AWS가 계정 제한 → EC2/NAT/워커 start 불가

### 교훈 (PPT bullet)
1. **표면 로그 ≠ 근본 원인** (Blocked ≠ Terraform 문법 오류)
2. 장기 Access Key 금지 → **GitHub OIDC**
3. `.env` / 깃에 키 금지 · MFA · Budgets
4. Support Resolved여도 제한 남을 수 있음 → 전담 에스컬레이션

### 한 장 도식 (말풍선)
```
.env에 iac-admin 키 노출
        ↓
  무단 RunInstances (CloudTrail)
        ↓
   AWS Account Blocked
        ↓
  StartInstances 전부 실패  ←── 우리가 본 증상
```

---

## 슬라이드 B — 왜 계정 이관을 했나

| Before | After |
|--------|--------|
| 구계정 Block으로 컴퓨트 기동 불가 | 신계정 `841535407395` 에 EKS·OIDC·ACM 재구축 |
| 포트폴리오/실습 일정 리스크 | GitOps(Argo)·Actions 경로 유지 |

**이관 ≠ 복사:** 리소스 ARN·레지스트리·DNS·IAM이 **전부 새 ID**.  
Git `values` / Actions Variables가 구계정을 가리키면 **증상만 바뀌며 계속 실패**.

---

## 슬라이드 C — 이관 직후 오류 맵 (한 장)

| # | 증상 (발표용) | 진짜 원인 | 한 줄 조치 |
|---|---------------|-----------|------------|
| 1 | 이미지 pull / 앱 안 뜸 | values·ECR이 **구 계정 레지스트리** | ECR URL·OIDC 역할 → 신계정 |
| 2 | HTTPS·ALB ADDRESS 없음 | **구 ACM ARN** 또는 새 인증서 **PENDING** | ISSUED 확인 후 HTTPS Ingress |
| 3 | `kubectl` / CI Unauthorized | Access Entry·OIDC trust 미이전 | CI 역할 ClusterAdmin Entry |
| 4 | helm `secrets required` | 빈 클러스터에 Secret 시드 없이 sync | Seed secrets → 그다음 Argo |
| 5 | Bind 후 Secret 깨짐 | helm upgrade가 **빈 secrets**로 덮어씀 | live Secret `--set-string` 주입 |
| 6 | Argo `Missing` | Job **sync-wave**가 Ingress Progressing에 막힘 **또는** SSA `terminatingReplicas` | wave 제거 · SSA 제거 |
| 7 | Cancel/재실행 안 됨 | `cancel-in-progress: false` / `cancelled()` 오용 | concurrency true · if:만 사용 |
| 8 | DB Actions 초록·데이터 없음 | migrate 빈 스키마 → Job **Skip** | 시드 행 검사 · Job 재실행 |
| 9 | apply 중반 Unauthorized | k8s provider 토큰 **15분 만료** | exec 인증으로 갱신 |
| 10 | 노드 NotReady / egress | **NAT 전에** 노드그룹 생성 | NAT·RT → 노드 |

---

## 슬라이드 D — HTTPS가 안 된 이유 (이관 대표 케이스)

### 제목
`ALB ADDRESS` 없음 = 서브넷 태그부터 의심하기 전에 **ACM 상태**

### 흐름
```
신계정 ACM 발급
    ↓
아직 PENDING_VALIDATION
    ↓
Ingress에 certificate-arn (HTTPS) 먼저 적용   ← 실수
    ↓
ALB Controller가 ADDRESS를 못 만듦
    ↓
「ALB 없다 / Bind 실패」로만 보임
```

### 교훈
- **ACM = ISSUED** 게이트 후에 HTTPS 어노테이션
- DNS validation(Route53) upsert 자동화
- 이관 체크리스트에 ACM ARN **계정 ID** 포함

---

## 슬라이드 E — Argo `Missing` 두 얼굴 (헷갈리기 쉬움)

발표에서 “같은 Missing인데 원인이 둘”을 강조하면 좋음.

| | A. sync-wave | B. ServerSideApply |
|--|--------------|---------------------|
| 보이는 것 | Job/`Missing` | ComparisonError · Missing |
| 원인 | Ingress가 ADDRESS 전 **Progressing** → 다음 wave Job 미적용 | SSA + `terminatingReplicas` 스키마 비교 실패 |
| 조치 | Job에 높은 wave 금지 | SSA 제거 · client-side apply · live options strip |

**교훈:** 증상 라벨(`Missing`)만 보고 한 가지 가설에 고정하지 말 것.

---

## 슬라이드 F — 「Actions 초록 = 복구 완료」 함정

### DB 시드 (이관 직후 빈 사이트)
- Verify DB restore **success**
- 로그: `table_count=25` → **Skip restore**
- 웹 `migrate`가 빈 테이블만 만듦 → 덤프 미적용
- 사이트: 「등록된 … 없습니다」

### 운영 교훈
1. 성공 조건 = HTTP 200이 아니라 **시드 행 / 목록 UI**
2. Job **Complete**면 덤프만 갈아끼워도 재실행 안 됨 → Job 삭제 후 Verify
3. SQL ≠ media → **Sync media → S3** 별도

---

## 슬라이드 G — 이관 체크리스트 (발표 마무리)

계정 옮긴 뒤 Git/CI에서 **계정 ID가 들어가는 것**만 다시 본다.

- [ ] ECR 레지스트리 URL (`8415…`)
- [ ] ACM 인증서 ARN + **ISSUED**
- [ ] Route53 존 / NS / ALB alias
- [ ] GitHub OIDC trust → 신계정 역할
- [ ] EKS Access Entry (CI · 관리자)
- [ ] S3 버킷명 (static/media)
- [ ] Helm values `image.repository` · `certificate-arn`
- [ ] K8s `aniverse-app-secrets` 시드
- [ ] (선택) DB dump main + Verify · media sync

**한 줄 마무리 멘트 예시**  
“계정 Block은 키가 원인이다. 이관 후에는 ARN을 안 고치면 Block과 다른 증상으로 같은 서비스가 또 죽는다.”

---

## 발표에 안 넣어도 되는 것 (시간 부족 시 생략)

- destroy state lock / VPC ENI / 노드그룹 DELETE_FAILED (destroy 시즌 이슈)
- EKS stop maxSize=0 · Autoscaler (비용 절감 운영)
- nginx `X-Forwarded-Proto` (HTTPS 세부)

원본·PR 번호는 troubleshooting-log 날짜 항목 참고 (2026-09-18 Blocked, 2026-09-22~23 이관 연쇄).

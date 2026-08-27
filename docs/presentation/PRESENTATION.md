# Aniverse 발표용 정리 — 온프레미스 → AWS + 자동화

> 도메인: https://aniverse.my  
> 앱: Django 6 / Channels / TMDB / Gemini  
> 인프라: Terraform (`anime-project-infra`) + CodeDeploy (`anime-project`)

---

## 1. 한 줄 스토리

**온프레미스에서 Nginx·Django·NFS·MariaDB 4대 서버로 돌리던 Aniverse를  
AWS 관리형 서비스로 옮기고, Terraform + GitHub Actions + CodeDeploy로  
인프라·배포를 자동화했다.**

---

## 2. Before (온프레미스 4-Tier)

| 서버 | 역할 |
|------|------|
| **Nginx** (DMZ) | 외부 진입, 정적/미디어, Reverse Proxy |
| **Django** (App) | Gunicorn/Daphne, 비즈니스 로직, Channels 채팅 |
| **NFS** | 미디어 공유 스토리지 (Nginx·Django 마운트) |
| **MariaDB** | 유저·작품·리뷰·거래 데이터 |

특징: 수동 설치·배포·백업. 스케일/장애 대응은 사람이 직접.

앱 구조(유지): `accounts` · `anime`(TMDB) · `deal`(채팅) · `works` · `community` · Gemini 챗봇

---

## 3. After (AWS) — 역할 매핑

| Before | After |
|--------|--------|
| Nginx 서버 | **ALB** + **ACM(HTTPS)** + **WAF** + EC2 내 Nginx |
| Django 서버 | **ASG EC2** (Daphne ASGI) + **ElastiCache Redis** (Channels) |
| NFS 서버 | **EFS** (공유 마운트) + **S3** (공개 미디어 URL) |
| MariaDB 서버 | **RDS MariaDB** + 스냅샷 |
| 수동 배포 | **GitHub Actions → S3 zip → CodeDeploy** |
| `.env` 파일 관리 | **Secrets Manager** (부팅 시 주입) |
| SSH 중심 운영 | **SSM Session Manager** (+ VPC Endpoint) |

추가된 것: Route 53(`aniverse.my`), HTTPS, WAF(Common/SQLi/Rate), ALB Access Logs, Terraform 모듈화

---

## 4. 자동화 파이프라인 (발표 포인트)

1. `main` 푸시 / workflow_dispatch  
2. media → public S3 sync  
3. 앱 zip → deploy S3  
4. CodeDeploy → ASG 인스턴스  
5. `install_dependencies` (migrate, collectstatic) → `start_server` (Daphne)

인프라 변경은 `anime-project-infra` Terraform Apply로 재현.

---

## 5. Before → After 비교 (발표용 한 장)

| 항목 | 온프레미스 | AWS |
|------|------------|-----|
| 서버 | 물리/VM 4대 고정 | 역할별 관리형 + ASG |
| HTTPS | 직접 인증서/설정 | ACM + ALB |
| 보안 | 방화벽/수동 | SG + WAF + Secrets |
| 미디어 | NFS | EFS + S3 |
| 채팅 확장 | 단일 프로세스 한계 | Redis Channel Layer |
| 배포 | SSH/수동 | GitHub Actions + CodeDeploy |
| 인프라 재현 | 문서/기억 | Terraform |
| 도메인 | 로컬/사설 | aniverse.my (Route 53) |

---

## 6. 발표에서 말할 “내가 한 일” (현우)

- 온프레미스 4-Tier 설계·서버 운영 경험 보유  
- AWS 이전: VPC / ALB / ASG / RDS / EFS / S3 / WAF / Secrets / Redis  
- IaC(Terraform)로 인프라 코드화  
- CI/CD로 push → 배포 자동화  
- 실장애 대응: CodeDeploy agent, DisallowedHost, DB restore env, static 403 권한, 미디어 S3 URL 등

---

## 7. 다이어그램 파일

| 파일 | 용도 |
|------|------|
| `docs/presentation/01-onprem-architecture.drawio` | 온프레미스 4서버 구조 |
| `docs/presentation/02-aws-architecture.drawio` | 현재 AWS 전체 구조 |
| `docs/presentation/03-migration-mapping.drawio` | Before→After 매핑 (발표 핵심 슬라이드) |

draw.io / diagrams.net 에서 열어 PNG·PDF로보내기 → 발표 슬라이드에 삽입.

---

## 8. 30초 클로징 멘트

> “기존에는 Nginx, Django, NFS, DB를 서버 네 대로 나눠 수동 운영했습니다.  
> 지금은 같은 역할을 ALB·ASG·EFS·S3·RDS로 옮기고,  
> Terraform과 GitHub Actions·CodeDeploy로 인프라와 배포를 자동화했습니다.  
> HTTPS·WAF·Secrets까지 기본 보안으로 넣었고, aniverse.my 로 서비스 중입니다.”

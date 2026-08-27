# Aniverse 발표용 정리 — 온프레미스 → AWS + 자동화

> 도메인: https://aniverse.my  
> 앱: Django 6 / Channels / TMDB / Gemini  
> 인프라: Terraform (`anime-project-infra`) + CodeDeploy (`anime-project`)

---

## 1. 한 줄 스토리

**온프레미스에서 Nginx·Django·NFS·MariaDB 4대 서버로 돌리던 Aniverse를  
AWS 관리형 서비스로 옮기고, Terraform + GitHub Actions + CodeDeploy로  
인프라·배포를 자동화했다.**

앱 기능 담당은 그대로, **클라우드 이전·자동화 단계에서는 인프라 역할로 재분담**했다.

---

## 2. Before (온프레미스 4-Tier)

| 서버 | 역할 |
|------|------|
| **Nginx** (DMZ) | 외부 진입, 정적/미디어, Reverse Proxy |
| **Django** (App) | Gunicorn/Daphne, 비즈니스 로직, Channels 채팅 |
| **NFS** | 미디어 공유 스토리지 (Nginx·Django 마운트) |
| **MariaDB** | 유저·작품·리뷰·거래 데이터 |

### 앱 기능 담당 (온프레미스·서비스 개발)

| 담당 | 역할 |
|------|------|
| **김현우** (팀장) | 로그인/회원가입, 애니메이션, 챗봇, TMDB·DB, 서버 구동 |
| **박서이** | 굿즈 거래·장터, 1:1 채팅 |
| **강유민** | 2차 창작물(코스프레/일러스트/소설) |
| **김윤주** | 커뮤니티 게시판 |

---

## 3. After (AWS) — 서비스 매핑

| Before | After |
|--------|--------|
| Nginx 서버 | **ALB** + **ACM(HTTPS)** + **WAF** + EC2 내 Nginx |
| Django 서버 | **ASG EC2** (Daphne ASGI) + **ElastiCache Redis** (Channels) |
| NFS 서버 | **EFS** (공유 마운트) + **S3** (공개 미디어 URL) |
| MariaDB 서버 | **RDS MariaDB** + 스냅샷 |
| 수동 배포 | **GitHub Actions → S3 zip → CodeDeploy** |
| `.env` 파일 관리 | **Secrets Manager** (부팅 시 주입) |
| SSH 중심 운영 | **SSM Session Manager** (+ VPC Endpoint) |

---

## 4. AWS 자동화 팀 역할 분담 (핵심 슬라이드)

| 담당 | 핵심 역할 | Terraform 모듈 | AWS 주요 서비스 | 세부 수행 업무 |
|------|-----------|-----------------|-----------------|----------------|
| **박서이** | Network & Security | `modules/network` · `modules/security` (+ NAT) | VPC, Subnet, IGW, NAT Instance, Security Group | 서울 리전 퍼블릭/프라이빗 망 분리·라우팅; 비용 절감용 NAT Instance(`t3.micro`); ALB–EC2–RDS–EFS 통신 SG 룰; `vpc_id` 등 outputs로 타 모듈 연결 |
| **강유민** | Compute & Traffic | `modules/compute` · `modules/alb` | ALB, Target Group, Launch Template, ASG | 외부 ALB·TG 구성; 프라이빗 EC2에 Nginx+앱(Daphne) 동시 기동 LT; EFS 마운트·Nginx `proxy_pass` 포함 `user_data.sh`; ASG 구성 |
| **김윤주** | Data & Storage | `modules/database` · `modules/storage` | RDS(MariaDB), EFS, S3 | S3+DynamoDB Remote State 초기 구축; RDS MariaDB; 다중 EC2용 EFS·마운트 타겟; 정적/미디어용 S3 |
| **김현우** | DevOps & CI/CD | `environments/dev` · GitHub Actions · `modules/cicd` 등 | GitHub Actions, CodeDeploy, CloudWatch, SSM | 1~3 모듈을 `environments/dev/main.tf`에서 조립·배포; infra/app 분리형 CI/CD; CloudWatch 알람·SSM 운영 연동 |

> 발표 시 포인트: **앱 기능 담당 ≠ 클라우드 모듈 담당**.  
> 온프레미스에선 페이지/기능, AWS 이전에서는 **네트워크 / 컴퓨팅 / 데이터 / 파이프라인**으로 나눔.

---

## 5. 자동화 파이프라인

1. `main` 푸시 / workflow_dispatch  
2. media → public S3 sync  
3. 앱 zip → deploy S3  
4. CodeDeploy → ASG  
5. migrate · collectstatic · Daphne 기동  

인프라 변경은 Terraform Apply로 재현.

---

## 6. Before → After 비교

| 항목 | 온프레미스 | AWS |
|------|------------|-----|
| 서버 | 물리/VM 4대 고정 | 역할별 관리형 + ASG |
| HTTPS | 직접 인증서 | ACM + ALB |
| 보안 | 방화벽/수동 | SG + WAF + Secrets |
| 미디어 | NFS | EFS + S3 |
| 채팅 | 단일 프로세스 | Redis Channel Layer |
| 배포 | SSH/수동 | Actions + CodeDeploy |
| 협업 | 서버 직접 접속 | 모듈 단위 PR + Remote State |
| 도메인 | 로컬/사설 | aniverse.my (Route 53) |

---

## 7. 현우(DevOps) 발표 포인트

- 팀 모듈을 `environments/dev`에서 **하나의 인프라로 통합**
- Django 앱(`anime-project`) / Terraform(`anime-project-infra`) **이중 파이프라인**
- CodeDeploy · SSM · CloudWatch로 **배포·접속·알람** 연결
- 운영 이슈 해결: agent 기동, healthcheck, DB restore env, static 권한, 미디어 S3 등

---

## 8. 다이어그램 파일

| 파일 | 용도 |
|------|------|
| `01-onprem-architecture.drawio` | 온프레미스 4서버 |
| `02-aws-architecture.drawio` | 현재 AWS 구조 |
| `03-migration-mapping.drawio` | Before→After 매핑 |
| `04-aws-team-roles.drawio` | **AWS 자동화 역할 분담** |

---

## 9. 30초 클로징

> “앱은 그대로 두고, 인프라는 네 명이 나눠 맡았습니다.  
> 서이가 네트워크·보안, 유민이 ALB·ASG 컴퓨팅, 윤주가 RDS·EFS·S3,  
> 저는 모듈을 조립하고 Terraform·GitHub Actions CI/CD로 자동화했습니다.  
> 그 결과 aniverse.my 에서 HTTPS와 자동 배포로 서비스 중입니다.”

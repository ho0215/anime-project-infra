# Aniverse 발표 대본 (통합)

> 보는 곳: **`VIEW.html`** 또는 **`ppt/Aniverse_발표_통합.pptx`**

---

## 1. 한 줄 스토리

온프레미스 Nginx·Django·NFS·MariaDB 4서버 → AWS 관리형 + Terraform/GitHub Actions/CodeDeploy 자동화.  
서비스: **https://aniverse.my**

---

## 2. Before → After

| 온프레미스 | AWS | 인프라 담당 |
|------------|-----|-------------|
| Nginx | ALB + ACM + WAF + EC2 Nginx | 유민 / 현우 |
| Django | ASG EC2 (Daphne) + Redis | 유민 |
| NFS | EFS + S3 | 윤주 |
| MariaDB | RDS + Secrets | 윤주 / 현우 |
| 수동 배포 | Actions + CodeDeploy / SSM | 현우 |
| 망·방화벽 | VPC · SG · NAT | 서이 |

---

## 3. 앱 담당 vs AWS 담당

| 이름 | 앱 (온프레미스) | AWS 자동화 |
|------|-----------------|------------|
| 김현우 | auth / anime / 챗봇 / 서버 | DevOps & CI/CD |
| 박서이 | deal / 채팅 | Network & Security |
| 강유민 | works | Compute & Traffic |
| 김윤주 | community | Data & Storage |

### AWS 세부

- **서이**: VPC/Subnet/IGW, NAT Instance(t3.micro), SG, outputs  
- **유민**: ALB/TG, LT/ASG, user_data(EFS·Nginx proxy)  
- **윤주**: Remote State, RDS, EFS, S3  
- **현우**: environments/dev 조립, infra/app CI/CD, CodeDeploy/SSM/CloudWatch, HTTPS·WAF·Secrets  

---

## 4. 런타임 스택

| 계층 | 구성 |
|------|------|
| Edge | Route53 · ACM · WAF · ALB HTTPS |
| App | nginx → Daphne → Django · Redis Channels |
| Data | RDS · EFS · S3 |
| Ops | Secrets · SSM · CodeDeploy · Actions |

---

## 5. 트러블슈팅 (기존 + 최근)

| 문제 | 해결 |
|------|------|
| CD 미동작 / TF 버전 | yml + TF 1.10.5 |
| ALB 혼재 | alb 모듈 + moved |
| 챗봇/WS | CSRF · Gemini · Daphne |
| 이미지 403 | S3 + bucket env |
| CodeDeploy/health | agent 조기설치 · /health/ |
| DB restore env | Secrets fallback |
| static/favicon 403 | /home/ubuntu 권한 |
| HTTPS | ACM + ALB 443 + WAF |

---

## 6. 30초 멘트

> 앱은 기능 담당으로 만들었고, 클라우드 이전에서는 역할을 다시 나눴습니다.  
> 서이 네트워크·보안, 유민 ALB·ASG, 윤주 RDS·EFS·S3,  
> 저는 모듈을 조립하고 Terraform·GitHub Actions로 자동화했습니다.  
> HTTPS·WAF·Secrets까지 넣었고, aniverse.my 로 서비스 중입니다.

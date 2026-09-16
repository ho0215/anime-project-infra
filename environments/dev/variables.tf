variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "project_name" {
  description = "리소스 이름 prefix (CodeDeploy/RDS/ALB 등)"
  type        = string
  default     = "aniverse"
}

variable "vpc_cidr" {
  description = "VPC 전체 IP 대역"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

# network 모듈 기본값과 반드시 일치 (기존 10.0.3/4 는 NAT SG 불일치 버그였음)
variable "private_app_subnet_cidrs" {
  description = "프라이빗 앱 서브넷 IP 대역"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "private_db_subnet_cidrs" {
  description = "프라이빗 DB 서브넷 IP 대역"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24"]
}

variable "admin_cidr_blocks" {
  description = "Bastion/관리자 접근 허용 CIDR"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "nat_ami" {
  description = "NAT 인스턴스 AMI (Amazon Linux 2, ap-northeast-2)"
  type        = string
  default     = "ami-0cde067c44daf99fc"
}

variable "static_bucket_name" {
  description = "정적/미디어 S3 버킷 base 이름 (뒤에 account-region 이 붙음)"
  type        = string
  default     = "aniverse-static-ho0215-dev-2026"
}

# ── Secrets 로만 주입 (기본값 없음) ─────────────────────
variable "db_password" {
  description = "RDS master password. GitHub Actions: TF_VAR_db_password"
  type        = string
  sensitive   = true
}

variable "django_secret_key" {
  description = "Django SECRET_KEY. GitHub Actions: TF_VAR_django_secret_key"
  type        = string
  sensitive   = true
}

variable "gemini_api_key" {
  description = "Gemini API key for AI chatbot. GitHub Actions: TF_VAR_gemini_api_key / secret TF_VAR_GEMINI_API_KEY"
  type        = string
  sensitive   = true
  default     = ""
}

# ── CodeDeploy 이름 (앱 저장소 deploy.yml 과 일치) ──────
variable "codedeploy_app_name" {
  type    = string
  default = "aniverse-app"
}

variable "codedeploy_group_name" {
  type    = string
  default = "aniverse-deployment-group"
}

variable "alert_email" {
  description = "비우면 monitoring 모듈을 생성하지 않음"
  type        = string
  default     = ""
}

variable "asg_desired_capacity" {
  type    = number
  default = 2
}

variable "asg_min_size" {
  type    = number
  default = 2
}

variable "asg_max_size" {
  type    = number
  default = 4
}

variable "domain_name" {
  description = "앱 도메인 (Route 53). enable_acm=true 이면 호스팅 영역이 이미 있어야 함"
  type        = string
  default     = "aniverse.my"
}

variable "subject_alternative_names" {
  description = "ACM SAN 목록"
  type        = list(string)
  default     = ["www.aniverse.my"]
}

# CD state 가 비어 있고 Route53 존이 없으면 ACM data source 가 plan 전체를 막음.
# EKS 전환 중: module.dns 가 존 생성. EC2 ALB HTTPS 는 enable_acm=true (ISSUED 후).
variable "enable_acm" {
  description = "기존 acm 모듈(ISSUED 대기) + EC2 ALB HTTPS. 보통 false — dns 모듈 사용"
  type        = bool
  default     = false
}

variable "create_route53_zone" {
  description = "퍼블릭 호스팅 영역 관리(true 유지). destroy 시 존은 keep-dns 스크립트·prevent_destroy 로 보존"
  type        = bool
  default     = true
}

variable "request_acm" {
  description = "ACM 인증서 + DNS 검증 레코드 생성 (ISSUED 대기는 안 함)"
  type        = bool
  default     = true
}

variable "eks_ingress_hostname" {
  description = "EKS Ingress ALB DNS 폴백 (lookup 실패 시). 비우면 태그만 사용 — 보통 비움"
  type        = string
  default     = ""
}

variable "lookup_eks_alb" {
  description = "Ingress 태그로 ALB 자동 조회 (재생성 후 apply 시 DNS 자동 갱신)"
  type        = bool
  default     = true
}

variable "eks_ingress_stack" {
  description = "AWS LB Controller stack 태그 = namespace/ingress-name"
  type        = string
  default     = "aniverse/aniverse-web"
}

variable "db_snapshot_identifier" {
  description = "RDS 복원 스냅샷 ID (GitHub: TF_VAR_db_snapshot_identifier / secret TF_VAR_DB_SNAPSHOT_IDENTIFIER)"
  type        = string
  default     = ""
}

variable "restore_from_latest_snapshot" {
  description = "최신 manual 스냅샷 자동 복원 (GitHub: TF_VAR_restore_from_latest_snapshot)"
  type        = bool
  default     = false
}

variable "waf_rate_limit" {
  description = "WAF IP당 5분 요청 한도"
  type        = number
  default     = 2000
}

variable "enable_waf" {
  type    = bool
  default = true
}

variable "enable_alb_access_logs" {
  type    = bool
  default = true
}

variable "enable_redis" {
  type    = bool
  default = true
}

variable "ecr_repository_name" {
  description = "ECR 리포지토리 이름 (앱 이미지)"
  type        = string
  default     = "aniverse"
}

variable "ecr_keep_image_count" {
  description = "ECR 라이프사이클으로 유지할 최대 이미지 수"
  type        = number
  default     = 20
}

# ==========================================
# EKS
# ==========================================
variable "eks_cluster_version" {
  description = "비워두면(null) AWS 기본(최신 지원) 버전 사용"
  type        = string
  default     = null
}

variable "eks_cluster_admin_arns" {
  description = "로컬 kubectl용 cluster-admin IAM ARN (GitHub OIDC 생성자는 bootstrap 으로 자동 포함)"
  type        = list(string)
  # cp1 기본 자격 증명 (aws sts get-caller-identity)
  default = [
    "arn:aws:iam::679583587966:user/iac-admin",
  ]
}

# scripts/eks-ctl.sh, .github/workflows/eks-start-stop.yml 기본값과 일치
variable "eks_node_desired_size" {
  type    = number
  default = 2
}

variable "eks_node_min_size" {
  type    = number
  default = 0
}

variable "eks_node_max_size" {
  type    = number
  default = 4
}

variable "eks_node_instance_types" {
  type    = list(string)
  default = ["t3.medium"]
}

variable "eks_node_capacity_type" {
  description = "ON_DEMAND | SPOT"
  type        = string
  default     = "ON_DEMAND"
}

variable "eks_enable_aws_lb_controller" {
  type    = bool
  default = true
}

variable "eks_enable_cluster_autoscaler" {
  type    = bool
  default = true
}


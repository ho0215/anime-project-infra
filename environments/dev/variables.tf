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
  description = "앱 도메인 (Route 53 호스팅 영역이 이미 있어야 함). 가비아 NS → Route 53 위임 후 사용"
  type        = string
  default     = "aniverse.my"
}

variable "subject_alternative_names" {
  description = "ACM SAN 목록"
  type        = list(string)
  default     = ["www.aniverse.my"]
}

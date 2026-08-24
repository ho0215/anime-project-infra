variable "aws_region" {
  description = "AWS 리전 (서울)"
  type        = string
  default     = "ap-northeast-2"
}

variable "vpc_cidr" {
  description = "VPC 전체 IP 대역"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_app_subnet_cidrs" {
  description = "프라이빗 앱 서브넷 IP 대역"
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "private_db_subnet_cidrs" {
  description = "프라이빗 DB 서브넷 IP 대역"
  type        = list(string)
  default     = ["10.0.5.0/24", "10.0.6.0/24"]
}

variable "admin_cidr_blocks" {
  description = "Bastion 호스트에 접근할 관리자 IP 대역"
  type        = list(string)
  default     = ["0.0.0.0/0"] # 배포 후 실제 작업자 IP로 변경 권장
}

variable "db_password" {
  description = "데이터베이스 비밀번호"
  type        = string
  sensitive   = true
  default     = "Aniverse1234!" # 테스트용 임시 비밀번호
}

variable "project_name" {
  type    = string
  default = "aniverse-ho0215-dev" # 버킷 이름이 aniverse-ho0215-dev-static 이 됩니다!
}
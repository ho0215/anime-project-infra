variable "project_name" {
  description = "프로젝트 이름 (리소스 네이밍 prefix)"
  type        = string
  default     = "aniverse"
}

variable "vpc_cidr" {
  description = "VPC CIDR 블록"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "사용할 가용영역 목록"
  type        = list(string)
  default     = ["ap-northeast-2a", "ap-northeast-2c"]
}

variable "public_subnet_cidrs" {
  description = "퍼블릭 서브넷 CIDR 목록 (ALB, NAT Gateway용)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "프라이빗 서브넷 CIDR 목록 (Django/Nginx EC2용)"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "private_db_subnet_cidrs" {
  description = "프라이빗 DB 서브넷 CIDR 목록 (MariaDB, Redis용)"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24"]
}

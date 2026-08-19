variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "vpc_id" {
  description = "network 모듈에서 받아오는 VPC ID"
  type        = string
}

variable "private_db_subnet_ids" {
  description = "RDS 배치할 프라이빗 DB 서브넷 ID 목록"
  type        = list(string)
}

variable "private_app_subnet_cidrs" {
  description = "Django 서버 서브넷 대역 (보안그룹 인바운드용)"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "db_name" {
  type    = string
  default = "aniverse"
}

variable "db_username" {
  type    = string
  default = "admin"
}

variable "db_password" {
  type      = string
  sensitive = true   # 비밀번호라 터미널에 안 찍힘
}
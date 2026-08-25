variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "vpc_id" {
  description = "network 모듈에서 받아오는 VPC ID (문서화용, RDS에는 직접 미사용)"
  type        = string
  default     = ""
}

variable "private_db_subnet_ids" {
  description = "RDS 배치할 프라이빗 DB 서브넷 ID 목록 (2개 AZ 이상 권장)"
  type        = list(string)
}

variable "db_sg_id" {
  description = "security 모듈에서 받아오는 DB 보안그룹 ID"
  type        = string
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
  sensitive = true
}

variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "vpc_id" {
  type = string
}

variable "private_app_subnet_ids" {
  description = "Django 서버 서브넷 ID (EFS 마운트 타겟용)"
  type        = list(string)
}

variable "private_app_subnet_cidrs" {
  description = "Django 서버 서브넷 대역 (보안그룹용)"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}
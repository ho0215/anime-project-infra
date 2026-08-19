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

variable "efs_sg_id" {
  description = "security 모듈에서 받아오는 EFS 보안그룹 ID"
  type        = string
}
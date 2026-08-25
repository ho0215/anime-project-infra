variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "ALB가 위치할 퍼블릭 서브넷들"
}

variable "alb_sg_id" {
  type        = string
  description = "ALB에 붙일 보안그룹 ID"
}

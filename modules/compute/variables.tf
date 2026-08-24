variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "private_app_subnet_ids" {
  type = list(string)
}

variable "alb_sg_id" {
  type = string
}

variable "app_sg_id" {
  type = string
}

variable "efs_dns_name" {
  type = string
}

variable "db_endpoint" {
  type = string
}
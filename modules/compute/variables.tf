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

variable "db_host" {
  description = "RDS 호스트명 (포트 제외)"
  type        = string
}

variable "db_port" {
  type    = number
  default = 3306
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

variable "static_bucket_name" {
  description = "미디어/정적 파일용 S3 버킷 이름"
  type        = string
}

variable "static_bucket_arn" {
  type = string
}

variable "deploy_bucket_arn" {
  description = "CodeDeploy 아티팩트 버킷 ARN"
  type        = string
  default     = ""
}

variable "django_secret_key" {
  type      = string
  sensitive = true
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
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

# 하위 호환: 예전 변수명 (미사용, 호출부 잔여 대비)
variable "db_endpoint" {
  type    = string
  default = ""
}

variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "private_app_subnet_ids" {
  type = list(string)
}

variable "app_sg_id" {
  type = string
}

variable "target_group_arn" {
  description = "ALB 타겟 그룹 ARN (modules/alb 출력)"
  type        = string
}

variable "efs_dns_name" {
  type = string
}

variable "static_bucket_arn" {
  type = string
}

variable "app_secret_arn" {
  description = "Secrets Manager ARN for runtime .env payload"
  type        = string
}

variable "deploy_bucket_arn" {
  description = "CodeDeploy 아티팩트 버킷 ARN"
  type        = string
  default     = ""
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

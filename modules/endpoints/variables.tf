variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "vpc_id" {
  type = string
}

variable "vpce_sg_id" {
  description = "security 모듈에서 만든 VPC endpoint(interface) SG"
  type        = string
}

variable "private_app_subnet_ids" {
  description = "SSM VPC endpoints are placed in private app subnets"
  type        = list(string)
}

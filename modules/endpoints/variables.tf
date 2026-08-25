variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "vpc_id" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "private_app_subnet_ids" {
  description = "SSM VPC endpoints are placed in private app subnets"
  type        = list(string)
}

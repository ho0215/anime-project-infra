variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "vpc_id" {
  description = "network VPC ID"
  type        = string
}

variable "private_app_subnet_cidrs" {
  description = "private app subnet CIDRs (NAT ingress allow)"
  type        = list(string)
}

variable "private_db_subnet_cidrs" {
  description = "legacy private DB subnet CIDRs (NAT ingress allow)"
  type        = list(string)
  default     = []
}

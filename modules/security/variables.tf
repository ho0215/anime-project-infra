variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "vpc_id" {
  description = "network VPC ID"
  type        = string
}

variable "vpc_cidr" {
  description = "network VPC CIDR"
  type        = string
}

variable "admin_cidr_blocks" {
  description = "team static IP" #관리자가 Bastion에 접속할 수 있는 IP 대역 (팀원 고정IP 등)
  type        = list(string)
  default     = ["0.0.0.0/0"]  # 실제 배포 전에 팀원 IP로 채워야 함
}

variable "private_app_subnet_cidrs" {
  description = "network private app subnet cidrs"
  type        = list(string)
}

variable "private_db_subnet_cidrs" {
  description = "network private db subnet cidrs"
  type        = list(string)
}
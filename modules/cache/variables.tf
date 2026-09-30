variable "project_name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_db_subnet_ids" {
  description = "ElastiCache subnet group — private-db 서브넷(module.network) 사용"
  type        = list(string)
}

variable "allowed_cidr_blocks" {
  description = "Redis(6379) 접근 허용 CIDR — EKS 파드가 있는 private-app 서브넷"
  type        = list(string)
}

variable "node_type" {
  description = "cache.t3.micro 등 — 소규모 팀 프로젝트 스케일 기준 기본값"
  type        = string
  default     = "cache.t3.micro"
}

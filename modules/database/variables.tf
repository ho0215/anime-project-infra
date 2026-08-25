variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "vpc_id" {
  description = "network 모듈에서 받아오는 VPC ID (문서화용, RDS에는 직접 미사용)"
  type        = string
  default     = ""
}

variable "private_db_subnet_ids" {
  description = "RDS 배치할 프라이빗 DB 서브넷 ID 목록 (2개 AZ 이상 권장)"
  type        = list(string)
}

variable "db_sg_id" {
  description = "security 모듈에서 받아오는 DB 보안그룹 ID"
  type        = string
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

variable "backup_retention_period" {
  description = "자동 백업 보관 일수 (0이면 자동 백업 비활성)"
  type        = number
  default     = 7
}

variable "deletion_protection" {
  description = "실수 destroy 방지. 개발 환경에서는 false 권장"
  type        = bool
  default     = false
}

# 빈 문자열이면 신규 생성. 스냅샷 ID를 넣으면 해당 스냅샷에서 복원.
variable "db_snapshot_identifier" {
  description = "복원할 RDS 스냅샷 ID. 빈 문자열이면 신규 생성"
  type        = string
  default     = "rds:test"
}

variable "restore_from_latest_snapshot" {
  description = "true 이면 aniverse-rds 의 최신 manual 스냅샷에서 복원. 스냅샷이 없으면 실패하므로 최초 배포는 false"
  type        = bool
  default     = true
}

variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "domain_name" {
  description = "apex 도메인 (예: aniverse.my). 기존 Route 53 퍼블릭 호스팅 영역이 있어야 함"
  type        = string
}

variable "subject_alternative_names" {
  description = "인증서 SAN (예: www.aniverse.my)"
  type        = list(string)
  default     = []
}

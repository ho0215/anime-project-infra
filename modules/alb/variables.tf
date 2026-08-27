variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "ALB가 위치할 퍼블릭 서브넷들"
}

variable "alb_sg_id" {
  type        = string
  description = "ALB에 붙일 보안그룹 ID"
}

variable "certificate_arn" {
  description = "ACM 인증서 ARN (enable_https=true 일 때 필수)"
  type        = string
  default     = ""
}

variable "enable_https" {
  description = "HTTPS 리스너 + HTTP→HTTPS redirect. count 에 쓰므로 plan-time 에 확정된 bool 이어야 함 (certificate_arn 직접 비교 금지)"
  type        = bool
  default     = true
}

variable "enable_access_logs" {
  description = "ALB access logs → S3"
  type        = bool
  default     = true
}

variable "idle_timeout" {
  description = "ALB 연결 유휴 타임아웃(초). WebSocket 채팅 연결이 조용히 끊기지 않도록 AWS 기본값(60)보다 넉넉히 잡는다."
  type        = number
  default     = 120
}

variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "alb_arn" {
  type        = string
  description = "연결할 ALB ARN"
}

variable "rate_limit" {
  description = "동일 IP 5분당 요청 한도"
  type        = number
  default     = 2000
}

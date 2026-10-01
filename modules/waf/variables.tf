variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "alb_arn" {
  type        = string
  description = "연결할 ALB ARN. 비우면 ACL만 생성(EKS는 Ingress wafv2-acl-arn 또는 다음 apply 때 연결)"
  default     = ""
}

variable "rate_limit" {
  description = "동일 IP 5분당 요청 한도"
  type        = number
  default     = 2000
}

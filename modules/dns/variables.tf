variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "aws_region" {
  type    = string
  default = "ap-northeast-2"
}

variable "domain_name" {
  type = string
}

variable "subject_alternative_names" {
  type    = list(string)
  default = []
}

variable "create_zone" {
  description = "true 면 퍼블릭 호스팅 영역 생성 (기존 존 없을 때). NS 를 가비아에 위임 필요"
  type        = bool
  default     = true
}

variable "eks_alb_dns_name" {
  description = "EKS Ingress ALB DNS (kubectl get ingress ...). 비우면 alias 레코드 안 만듦"
  type        = string
  default     = ""
}

variable "request_acm" {
  description = "ACM 인증서 + DNS 검증 레코드 생성 (ISSUED 대기는 안 함)"
  type        = bool
  default     = true
}

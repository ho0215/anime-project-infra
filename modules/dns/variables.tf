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
  description = "true 면 퍼블릭 호스팅 영역 생성(최초 1회). 이후에도 true 유지해도 destroy 시 존은 보존"
  type        = bool
  default     = true
}

variable "eks_alb_dns_name" {
  description = "EKS Ingress ALB DNS 폴백. lookup_eks_alb 실패 시에만 사용"
  type        = string
  default     = ""
}

variable "lookup_eks_alb" {
  description = "Ingress 태그(ingress.k8s.aws/stack)로 ALB 자동 조회"
  type        = bool
  default     = true
}

variable "eks_ingress_stack" {
  description = "AWS LB Controller stack 태그 = {namespace}/{ingress-name}"
  type        = string
  default     = "aniverse/aniverse-web"
}

variable "request_acm" {
  description = "ACM 인증서 + DNS 검증 레코드 생성 (ISSUED 대기는 안 함)"
  type        = bool
  default     = true
}

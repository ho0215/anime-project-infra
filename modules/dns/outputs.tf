output "zone_id" {
  value = local.zone_id
}

output "name_servers" {
  description = "가비아에 등록할 NS (존을 지우지 않는 한 고정)"
  value       = local.name_servers
}

output "domain_name" {
  value = var.domain_name
}

output "certificate_arn" {
  description = "ACM ARN (NS 위임 전엔 Pending Validation 일 수 있음)"
  value       = var.request_acm ? aws_acm_certificate.main[0].arn : null
}

output "app_url" {
  value = "https://${var.domain_name}"
}

output "eks_alb_dns_name" {
  description = "현재 Route53 alias 가 가리키는 ALB DNS"
  value       = local.eks_alb_dns != "" ? local.eks_alb_dns : null
}

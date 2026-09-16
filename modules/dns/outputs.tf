output "zone_id" {
  value = local.zone_id
}

output "name_servers" {
  description = "가비아에 등록할 NS"
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

output "eks_apex_fqdn" {
  value = var.eks_alb_dns_name != "" ? var.domain_name : null
}

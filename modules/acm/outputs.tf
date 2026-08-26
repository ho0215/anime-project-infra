output "certificate_arn" {
  description = "검증 완료된 ACM 인증서 ARN (ALB HTTPS 리스너용)"
  value       = aws_acm_certificate_validation.main.certificate_arn
}

output "zone_id" {
  value = data.aws_route53_zone.main.zone_id
}

output "domain_name" {
  value = var.domain_name
}

output "app_url" {
  value = "https://${var.domain_name}"
}

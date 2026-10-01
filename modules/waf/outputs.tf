output "web_acl_arn" {
  description = "Ingress annotation alb.ingress.kubernetes.io/wafv2-acl-arn 에 넣을 ARN"
  value       = aws_wafv2_web_acl.main.arn
}

output "web_acl_id" {
  value = aws_wafv2_web_acl.main.id
}

output "web_acl_name" {
  value = aws_wafv2_web_acl.main.name
}

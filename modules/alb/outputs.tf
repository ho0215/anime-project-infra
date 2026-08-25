output "alb_dns_name" {
  description = "웹 브라우저로 접속할 ALB 주소"
  value       = aws_lb.main.dns_name
}

output "alb_url" {
  value = "http://${aws_lb.main.dns_name}"
}

output "alb_arn" {
  value = aws_lb.main.arn
}

output "alb_arn_suffix" {
  description = "모니터링 알람에 연결할 ALB Suffix"
  value       = aws_lb.main.arn_suffix
}

output "target_group_arn" {
  value = aws_lb_target_group.app.arn
}

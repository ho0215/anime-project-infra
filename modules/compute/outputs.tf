output "alb_dns_name" {
  description = "ALB 접속 주소 (사용자가 접속하는 URL)"
  value       = aws_lb.app.dns_name
}

output "target_group_arn" {
  value = aws_lb_target_group.app.arn
}

output "asg_name" {
  value = aws_autoscaling_group.app.name
}

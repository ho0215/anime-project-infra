output "alb_dns_name" {
  description = "웹 브라우저로 접속할 ALB 주소"
  value       = aws_lb.main.dns_name
}

output "alb_url" {
  value = "http://${aws_lb.main.dns_name}"
}

output "asg_name" {
  description = "CodeDeploy / 모니터링에 연결할 ASG 이름"
  value       = aws_autoscaling_group.app.name
}

output "alb_arn_suffix" {
  description = "모니터링 알람에 연결할 ALB Suffix"
  value       = aws_lb.main.arn_suffix
}

output "app_instance_profile_name" {
  value = aws_iam_instance_profile.app_profile.name
}

output "app_role_name" {
  value = aws_iam_role.app_role.name
}

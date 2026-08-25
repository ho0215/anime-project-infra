output "asg_name" {
  description = "CodeDeploy / 모니터링에 연결할 ASG 이름"
  value       = aws_autoscaling_group.app.name
}

output "app_instance_profile_name" {
  value = aws_iam_instance_profile.app_profile.name
}

output "app_role_name" {
  value = aws_iam_role.app_role.name
}

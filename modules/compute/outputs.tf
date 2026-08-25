output "asg_name" {
  value = aws_autoscaling_group.app.name
}

output "launch_template_id" {
  value = aws_launch_template.app.id
}

output "iam_role_name" {
  value = aws_iam_role.ec2_ssm_role.name
}
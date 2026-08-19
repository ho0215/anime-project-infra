output "efs_id" {
  value = aws_efs_file_system.main.id
}

output "efs_dns_name" {
  description = "Django 서버에서 마운트할 때 쓰는 DNS"
  value       = aws_efs_file_system.main.dns_name
}

output "efs_sg_id" {
  value = aws_security_group.efs.id
}
output "rds_endpoint" {
  description = "Django .env에 넣을 RDS 엔드포인트"
  value       = aws_db_instance.main.endpoint
}

output "rds_sg_id" {
  description = "RDS 보안그룹 ID"
  value       = aws_security_group.rds.id
}
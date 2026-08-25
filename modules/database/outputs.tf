output "rds_endpoint" {
  description = "Django .env에 넣을 RDS 엔드포인트"
  value       = aws_db_instance.main.endpoint
}

output "rds_port" {
  description = "RDS 포트"
  value       = aws_db_instance.main.port
}
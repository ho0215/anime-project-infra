output "rds_endpoint" {
  description = "Django .env에 넣을 RDS 엔드포인트"
  value       = aws_db_instance.main.endpoint
}
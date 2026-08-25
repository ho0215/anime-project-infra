output "rds_endpoint" {
  description = "Django .env에 넣을 RDS 엔드포인트 (host:port)"
  value       = aws_db_instance.main.endpoint
}

output "rds_address" {
  description = "RDS 호스트명 (포트 제외)"
  value       = aws_db_instance.main.address
}

output "rds_port" {
  description = "RDS 포트"
  value       = aws_db_instance.main.port
}

output "rds_identifier" {
  description = "RDS 인스턴스 식별자"
  value       = aws_db_instance.main.identifier
}

output "db_subnet_group_name" {
  value = aws_db_subnet_group.main.name
}

output "restored_from_snapshot" {
  description = "복원에 사용된 스냅샷 ID (없으면 null)"
  value       = local.effective_snapshot_id
}

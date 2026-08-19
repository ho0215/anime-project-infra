output "efs_id" {
  value = aws_efs_file_system.main.id
}

output "efs_dns_name" {
  description = "Django 서버에서 마운트할 때 쓰는 DNS"
  value       = aws_efs_file_system.main.dns_name
}

output "s3_bucket_name" {
  value = aws_s3_bucket.static.bucket
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.static.arn
}
output "repository_url" {
  description = "docker tag/push 에 쓰는 레지스트리 URL (계정.dkr.ecr.리전.amazonaws.com/이름)"
  value       = aws_ecr_repository.app.repository_url
}

output "repository_arn" {
  value = aws_ecr_repository.app.arn
}

output "repository_name" {
  value = aws_ecr_repository.app.name
}

output "registry_id" {
  value = aws_ecr_repository.app.registry_id
}

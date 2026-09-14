output "tfstate_bucket_name" {
  value = aws_s3_bucket.tfstate.bucket
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.terraform_lock.name
}

output "github_actions_role_arn" {
  description = "infra 레포 Variable AWS_ROLE_ARN (Terraform Admin OIDC)"
  value       = aws_iam_role.github_actions.arn
}

output "github_actions_app_ecr_role_arn" {
  description = "anime-project Variable AWS_ROLE_ARN (ECR push OIDC)"
  value       = aws_iam_role.github_actions_app_ecr.arn
}
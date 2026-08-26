output "tfstate_bucket_name" {
  value = aws_s3_bucket.tfstate.bucket
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.terraform_lock.name
}

output "github_actions_role_arn" {
  description = "GitHub Actions Variable AWS_ROLE_ARN 에 넣을 값"
  value       = aws_iam_role.github_actions.arn
}
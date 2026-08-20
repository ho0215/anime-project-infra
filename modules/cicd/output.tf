output "deploy_bucket_name" {
  description = "GitHub Actions가 압축 파일을 업로드할 S3 버킷 이름"
  value       = aws_s3_bucket.deploy_bucket.bucket
}

output "codedeploy_app_name" {
  description = "CodeDeploy 애플리케이션 이름"
  value       = aws_codedeploy_app.app.name
}

output "codedeploy_group_name" {
  description = "CodeDeploy 배포 그룹 이름"
  value       = aws_codedeploy_deployment_group.dg.deployment_group_name
}

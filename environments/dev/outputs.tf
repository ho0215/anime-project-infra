output "alb_dns_name" {
  description = "애플리케이션 접속용 ALB DNS"
  value       = module.compute.alb_dns_name
}

output "alb_url" {
  value = module.compute.alb_url
}

output "rds_endpoint" {
  value = module.database.rds_endpoint
}

output "rds_address" {
  value = module.database.rds_address
}

output "static_bucket_name" {
  value = module.storage.s3_bucket_name
}

output "deploy_bucket_name" {
  description = "GitHub Secret S3_BUCKET_NAME 에 등록할 값"
  value       = module.cicd.deploy_bucket_name
}

output "codedeploy_app_name" {
  value = module.cicd.codedeploy_app_name
}

output "codedeploy_group_name" {
  value = module.cicd.codedeploy_group_name
}

output "asg_name" {
  value = module.compute.asg_name
}

output "efs_dns_name" {
  value = module.storage.efs_dns_name
}

output "restored_from_snapshot" {
  value = module.database.restored_from_snapshot
}

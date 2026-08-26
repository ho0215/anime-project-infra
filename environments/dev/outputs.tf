output "alb_dns_name" {
  description = "애플리케이션 접속용 ALB DNS"
  value       = module.alb.alb_dns_name
}

output "alb_url" {
  value = module.alb.alb_url
}

output "app_url" {
  description = "HTTPS 앱 URL (도메인)"
  value       = module.acm.app_url
}

output "certificate_arn" {
  value = module.acm.certificate_arn
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

output "ssm_endpoint_ids" {
  description = "Private SSM VPC endpoint IDs (ssm / ssmmessages / ec2messages)"
  value       = module.endpoints.ssm_endpoint_ids
}

output "ssm_connect_hint" {
  description = "Local command to open an SSM shell on an ASG instance"
  value       = "ASG_NAME=${module.compute.asg_name} ./scripts/ssm-connect.sh"
}

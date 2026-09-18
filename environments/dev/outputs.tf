output "app_url" {
  description = "앱 URL (HTTPS — Ingress ACM)"
  value       = "https://${var.domain_name}"
}

output "certificate_arn" {
  description = "dns 모듈 ACM (Pending 일 수 있음)"
  value       = module.dns.certificate_arn
}

output "route53_zone_id" {
  value = module.dns.zone_id
}

output "route53_name_servers" {
  description = "가비아에 넣을 NS"
  value       = module.dns.name_servers
}

output "eks_ingress_hostname" {
  description = "폴백 변수 값 (참고)"
  value       = var.eks_ingress_hostname
}

output "eks_alb_dns_resolved" {
  description = "Route53 이 가리키는 ALB DNS"
  value       = module.dns.eks_alb_dns_name
}

output "static_bucket_name" {
  value = module.storage.s3_bucket_name
}

output "ecr_repository_url" {
  value = module.ecr.repository_url
}

output "ecr_repository_name" {
  value = module.ecr.repository_name
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_kubeconfig_hint" {
  value = module.eks.kubeconfig_hint
}

output "eks_node_role_arn" {
  value = module.eks.node_role_arn
}

output "app_s3_irsa_role_arn" {
  description = "anime-project values-eks.yaml serviceAccount.annotations role-arn"
  value       = module.eks.app_s3_irsa_role_arn
}

output "db_backup_irsa_role_arn" {
  description = "윤주 백업 CronJob ServiceAccount(aniverse-db-backup)에 붙일 role-arn"
  value       = module.eks.db_backup_irsa_role_arn
}

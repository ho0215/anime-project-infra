output "cluster_name" {
  value = aws_eks_cluster.this.name
}

output "cluster_endpoint" {
  value = aws_eks_cluster.this.endpoint
}

output "cluster_ca_certificate" {
  value = aws_eks_cluster.this.certificate_authority[0].data
}

output "cluster_arn" {
  value = aws_eks_cluster.this.arn
}

output "node_group_name" {
  value = aws_eks_node_group.default.node_group_name
}

output "node_role_arn" {
  value = aws_iam_role.node.arn
}

output "oidc_provider_arn" {
  value = aws_iam_openid_connect_provider.eks.arn
}

output "ebs_csi_role_arn" {
  value = aws_iam_role.ebs_csi.arn
}

output "lb_controller_role_arn" {
  value = var.enable_aws_lb_controller ? aws_iam_role.lb_controller[0].arn : null
}

output "app_s3_irsa_role_arn" {
  description = "aniverse-web SA 에 붙일 IAM 역할 (values-eks serviceAccount.annotations)"
  value       = var.enable_app_s3_irsa ? aws_iam_role.app_s3[0].arn : null
}

output "db_backup_irsa_role_arn" {
  description = "백업 CronJob ServiceAccount(aniverse-db-backup)에 붙일 IAM role"
  value       = var.enable_db_backup_irsa ? aws_iam_role.db_backup[0].arn : null
}

output "kubeconfig_hint" {
  description = "로컬에서 kubectl 붙일 때"
  value       = "aws eks update-kubeconfig --region ${data.aws_region.current.name} --name ${aws_eks_cluster.this.name}"
}

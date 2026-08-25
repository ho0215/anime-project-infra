# ==========================================
# Network / NAT / Security
# ==========================================
module "network" {
  source = "../../modules/network"

  project_name             = var.project_name
  vpc_cidr                 = var.vpc_cidr
  public_subnet_cidrs      = var.public_subnet_cidrs
  private_app_subnet_cidrs = var.private_app_subnet_cidrs
  private_db_subnet_cidrs  = var.private_db_subnet_cidrs
  nat_network_interface_id = module.nat.primary_network_interface_id
}

module "security" {
  source = "../../modules/security"

  project_name             = var.project_name
  vpc_id                   = module.network.vpc_id
  vpc_cidr                 = var.vpc_cidr
  private_app_subnet_cidrs = var.private_app_subnet_cidrs
  private_db_subnet_cidrs  = var.private_db_subnet_cidrs
  admin_cidr_blocks        = var.admin_cidr_blocks
}

module "nat" {
  source = "../../modules/nat"

  project_name     = var.project_name
  nat_ami          = var.nat_ami
  public_subnet_id = module.network.public_subnet_ids[0]
  nat_sg_id        = module.security.nat_sg_id
}

# SSM Session Manager: private EC2 ↔ AWS (NAT 장애에도 접속 가능)
module "endpoints" {
  source = "../../modules/endpoints"

  project_name           = var.project_name
  vpc_id                 = module.network.vpc_id
  vpc_cidr               = var.vpc_cidr
  private_app_subnet_ids = module.network.private_app_subnet_ids
}

# ==========================================
# Database & Storage
# ==========================================
module "database" {
  source = "../../modules/database"

  project_name          = var.project_name
  vpc_id                = module.network.vpc_id
  private_db_subnet_ids = module.network.private_db_subnet_ids
  db_sg_id              = module.security.db_sg_id
  db_password           = var.db_password

  # RDS 영속성 옵션 — environments/dev/variables.tf 에 선언됨
  # (TF_VAR_db_snapshot_identifier / TF_VAR_restore_from_latest_snapshot 등으로 덮어쓰기)
  db_snapshot_identifier       = var.db_snapshot_identifier
  restore_from_latest_snapshot = var.restore_from_latest_snapshot
  backup_retention_period      = var.backup_retention_period
  deletion_protection          = var.deletion_protection
}

module "storage" {
  source = "../../modules/storage"

  project_name           = var.project_name
  vpc_id                 = module.network.vpc_id
  private_app_subnet_ids = module.network.private_app_subnet_ids
  efs_sg_id              = module.security.efs_sg_id
  bucket_name            = var.static_bucket_name
}

# ==========================================
# ALB (퍼블릭 로드밸런서 / 타겟 그룹 / 리스너)
# ==========================================
module "alb" {
  source = "../../modules/alb"

  project_name      = var.project_name
  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids
  alb_sg_id         = module.security.alb_sg_id
}

# ==========================================
# Compute (ASG / Launch Template / IAM)
# ==========================================
module "compute" {
  source = "../../modules/compute"

  project_name           = var.project_name
  private_app_subnet_ids = module.network.private_app_subnet_ids
  app_sg_id              = module.security.app_sg_id
  target_group_arn       = module.alb.target_group_arn
  efs_dns_name           = module.storage.efs_dns_name
  db_host                = module.database.rds_address
  db_port                = module.database.rds_port
  db_name                = "aniverse"
  db_username            = "admin"
  db_password            = var.db_password
  static_bucket_name     = module.storage.s3_bucket_name
  static_bucket_arn      = module.storage.s3_bucket_arn
  django_secret_key      = var.django_secret_key
  gemini_api_key         = var.gemini_api_key
  asg_desired_capacity   = var.asg_desired_capacity
  asg_min_size           = var.asg_min_size
  asg_max_size           = var.asg_max_size
}

# ==========================================
# CI/CD (CodeDeploy + deploy S3) — 기존에 미연결
# ==========================================
module "cicd" {
  source = "../../modules/cicd"

  project_name          = var.project_name
  asg_name              = module.compute.asg_name
  app_role_name         = module.compute.app_role_name
  codedeploy_app_name   = var.codedeploy_app_name
  codedeploy_group_name = var.codedeploy_group_name
}

# ==========================================
# Monitoring (옵션: alert_email 이 있을 때만)
# ==========================================
module "monitoring" {
  count  = var.alert_email != "" ? 1 : 0
  source = "../../modules/monitoring"

  project_name   = var.project_name
  alert_email    = var.alert_email
  asg_name       = module.compute.asg_name
  alb_arn_suffix = module.alb.alb_arn_suffix
}

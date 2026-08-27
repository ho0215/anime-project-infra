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
  vpce_sg_id             = module.security.vpce_sg_id
  private_app_subnet_ids = module.network.private_app_subnet_ids
}

# ==========================================
# Database & Storage
# ==========================================
module "database" {
  source = "../../modules/database"

  project_name                 = var.project_name
  vpc_id                       = module.network.vpc_id
  private_db_subnet_ids        = module.network.private_db_subnet_ids
  db_sg_id                     = module.security.db_sg_id
  db_password                  = var.db_password
  db_snapshot_identifier       = var.db_snapshot_identifier
  restore_from_latest_snapshot = var.restore_from_latest_snapshot
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
# ACM (기존 Route 53 호스팅 영역 + DNS 검증)
# ==========================================
module "acm" {
  source = "../../modules/acm"

  project_name              = var.project_name
  domain_name               = var.domain_name
  subject_alternative_names = var.subject_alternative_names
}

# ==========================================
# ALB (퍼블릭 로드밸런서 / 타겟 그룹 / HTTPS)
# ==========================================
module "alb" {
  source = "../../modules/alb"

  project_name       = var.project_name
  vpc_id             = module.network.vpc_id
  public_subnet_ids  = module.network.public_subnet_ids
  alb_sg_id          = module.security.alb_sg_id
  certificate_arn    = module.acm.certificate_arn
  enable_https       = true
  enable_access_logs = var.enable_alb_access_logs
}

# apex / www → ALB (ACM 과 ALB 순환 참조 방지를 위해 루트에 둠)
resource "aws_route53_record" "apex" {
  zone_id = module.acm.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = module.alb.alb_dns_name
    zone_id                = module.alb.alb_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "www" {
  count = contains(var.subject_alternative_names, "www.${var.domain_name}") ? 1 : 0

  zone_id = module.acm.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name                   = module.alb.alb_dns_name
    zone_id                = module.alb.alb_zone_id
    evaluate_target_health = true
  }
}

# ==========================================
# WAF (ALB 연결)
# ==========================================
module "waf" {
  count  = var.enable_waf ? 1 : 0
  source = "../../modules/waf"

  project_name = var.project_name
  alb_arn      = module.alb.alb_arn
  rate_limit   = var.waf_rate_limit
}

# ==========================================
# Redis (Django Channels)
# ==========================================
module "redis" {
  count  = var.enable_redis ? 1 : 0
  source = "../../modules/redis"

  project_name           = var.project_name
  private_app_subnet_ids = module.network.private_app_subnet_ids
  redis_sg_id            = module.security.redis_sg_id
}

# ==========================================
# Secrets Manager (EC2 가 부팅 시 .env 로 로드)
# ==========================================
module "secrets" {
  source = "../../modules/secrets"

  project_name       = var.project_name
  django_secret_key  = var.django_secret_key
  db_password        = var.db_password
  gemini_api_key     = var.gemini_api_key
  db_host            = module.database.rds_address
  db_port            = module.database.rds_port
  static_bucket_name = module.storage.s3_bucket_name
  aws_region         = var.aws_region
  domain_name        = var.domain_name
  use_https          = true
  redis_url          = var.enable_redis ? module.redis[0].redis_url : ""
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
  static_bucket_arn      = module.storage.s3_bucket_arn
  app_secret_arn         = module.secrets.secret_arn
  asg_desired_capacity   = var.asg_desired_capacity
  asg_min_size           = var.asg_min_size
  asg_max_size           = var.asg_max_size
}

# ==========================================
# CI/CD (CodeDeploy + deploy S3)
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

  project_name            = var.project_name
  alert_email             = var.alert_email
  asg_name                = module.compute.asg_name
  alb_arn_suffix          = module.alb.alb_arn_suffix
  target_group_arn_suffix = module.alb.target_group_arn_suffix
}

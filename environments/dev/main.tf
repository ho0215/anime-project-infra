# EKS-only stack: VPC + NAT + S3 static + Route53/ACM + ECR + EKS
# (EC2 ASG / CodeDeploy / RDS / Redis / EFS / classic ALB 제거)

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
  private_app_subnet_cidrs = var.private_app_subnet_cidrs
  private_db_subnet_cidrs  = var.private_db_subnet_cidrs
}

module "nat" {
  source = "../../modules/nat"

  project_name     = var.project_name
  nat_ami          = var.nat_ami
  public_subnet_id = module.network.public_subnet_ids[0]
  nat_sg_id        = module.security.nat_sg_id
}

# ==========================================
# Storage (S3 static/media only — EFS 제거)
# ==========================================
module "storage" {
  source = "../../modules/storage"

  project_name = var.project_name
  bucket_name  = var.static_bucket_name
}

# ==========================================
# DNS (Route53 zone + EKS ALB alias + ACM)
# destroy 시 존·ACM 보존: scripts/terraform-destroy-keep-dns.sh
# ==========================================
module "dns" {
  source = "../../modules/dns"

  project_name              = var.project_name
  aws_region                = var.aws_region
  domain_name               = var.domain_name
  subject_alternative_names = var.subject_alternative_names
  create_zone               = var.create_route53_zone
  eks_alb_dns_name          = var.eks_ingress_hostname
  lookup_eks_alb            = var.lookup_eks_alb
  eks_ingress_stack         = var.eks_ingress_stack
  request_acm               = var.request_acm
}

# ==========================================
# ECR
# ==========================================
module "ecr" {
  source = "../../modules/ecr"

  project_name     = var.project_name
  repository_name  = var.ecr_repository_name
  keep_image_count = var.ecr_keep_image_count
}

# ==========================================
# EKS
# ==========================================
module "eks" {
  source = "../../modules/eks"

  project_name           = var.project_name
  vpc_id                 = module.network.vpc_id
  vpc_cidr               = var.vpc_cidr
  public_subnet_ids      = module.network.public_subnet_ids
  private_app_subnet_ids = module.network.private_app_subnet_ids

  cluster_version             = var.eks_cluster_version
  cluster_public_access_cidrs = var.admin_cidr_blocks
  cluster_admin_arns          = var.eks_cluster_admin_arns

  node_desired_size   = var.eks_node_desired_size
  node_min_size       = var.eks_node_min_size
  node_max_size       = var.eks_node_max_size
  node_instance_types = var.eks_node_instance_types
  node_capacity_type  = var.eks_node_capacity_type

  enable_aws_lb_controller  = var.eks_enable_aws_lb_controller
  enable_cluster_autoscaler = var.eks_enable_cluster_autoscaler

  # web Pod IRSA — Helm values-eks serviceAccount.annotations
  enable_app_s3_irsa = true
  app_s3_bucket_arn  = module.storage.s3_bucket_arn

  # DB 백업(mysqldump) CronJob IRSA — 같은 버킷의 db-backups/ prefix로만 권한 제한
  enable_db_backup_irsa   = true
  db_backup_s3_bucket_arn = module.storage.s3_bucket_arn
}

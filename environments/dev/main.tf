# ==========================================
# 팀원 1: Network, NAT, Security
# ==========================================
module "network" {
  source                   = "../../modules/network"
  vpc_cidr                 = var.vpc_cidr
  nat_network_interface_id = module.nat.primary_network_interface_id
}

module "security" {
  source                   = "../../modules/security"
  vpc_id                   = module.network.vpc_id
  vpc_cidr                 = var.vpc_cidr
  private_app_subnet_cidrs = var.private_app_subnet_cidrs
  private_db_subnet_cidrs  = var.private_db_subnet_cidrs
  admin_cidr_blocks        = var.admin_cidr_blocks
}

module "nat" {
  # 1. 모듈 경로 (실수로 지워졌던 부분)
  source           = "../../modules/nat"
  
  # 2. 이번에 추가해야 할 필수 변수 2가지
  project_name     = "aniverse"
  nat_ami          = "ami-0cde067c44daf99fc" # 서울 리전의 Amazon Linux 2 최신 이미지
  
  # 3. 기존에 있던 네트워크 및 보안 그룹 연결 고리
  public_subnet_id = module.network.public_subnet_ids[0]
  nat_sg_id        = module.security.nat_sg_id
}

# ==========================================
# 팀원 3: Database & Storage
# ==========================================
module "database" {
  source                = "../../modules/database"
  vpc_id                = module.network.vpc_id
  private_db_subnet_ids = module.network.private_db_subnet_ids
  db_sg_id              = module.security.db_sg_id
  db_password           = var.db_password
}

module "storage" {
  source                 = "../../modules/storage"
  vpc_id                 = module.network.vpc_id
  private_app_subnet_ids = module.network.private_app_subnet_ids
  efs_sg_id              = module.security.efs_sg_id

  # 전 세계에서 유일한 나만의 버킷 이름 지정!
  bucket_name            = "aniverse-static-ho0215-dev-2026"
}

# ==========================================
# 팀원 2: Compute & Traffic
# ==========================================
module "compute" {
  source                   = "../../modules/compute"
  vpc_id                   = module.network.vpc_id
  public_subnet_ids        = module.network.public_subnet_ids
  private_app_subnet_ids   = module.network.private_app_subnet_ids
  alb_sg_id                = module.security.alb_sg_id
  app_sg_id                = module.security.app_sg_id
  efs_dns_name             = module.storage.efs_dns_name
  db_endpoint              = module.database.rds_endpoint
}
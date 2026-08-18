# ==========================================
# 팀원 1: Network & Security
# ==========================================
# module "network" {
#   source   = "../../modules/network"
#   vpc_cidr = var.vpc_cidr
# }

# module "security" {
#   source = "../../modules/security"
#   vpc_id = module.network.vpc_id
# }

# ==========================================
# 팀원 3: Database & Storage
# ==========================================
# module "database" {
#   source          = "../../modules/database"
#   private_subnets = module.network.private_db_subnets
#   rds_sg_id       = module.security.rds_sg_id
# }

# module "storage" {
#   source          = "../../modules/storage"
#   private_subnets = module.network.private_app_subnets
#   efs_sg_id       = module.security.efs_sg_id
# }

# ==========================================
# 팀원 2: Compute & Traffic
# ==========================================
# module "compute" {
#   source          = "../../modules/compute"
#   vpc_id          = module.network.vpc_id
#   public_subnets  = module.network.public_subnets
#   private_subnets = module.network.private_app_subnets
#   alb_sg_id       = module.security.alb_sg_id
#   app_sg_id       = module.security.app_sg_id
#   efs_dns_name    = module.storage.efs_dns_name
#   db_endpoint     = module.database.rds_endpoint
# }
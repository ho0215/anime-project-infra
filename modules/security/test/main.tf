provider "aws" {
  region = "ap-northeast-2"
}

module "my_security_test" {
  source = "../"

  vpc_id                   = "sg-0197912fe68200772"
  vpc_cidr                 = "10.0.0.0/16"
  private_app_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]
  private_db_subnet_cidrs  = ["10.0.21.0/24", "10.0.22.0/24"]
}

output "test_alb_sg_id" {
  value = module.my_security_test.alb_sg_id   # outputs.tf에 있는 이름으로 맞춰서
}

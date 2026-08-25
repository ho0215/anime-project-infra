# 1. 임시 프로바이더 설정
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "aws" {
  region = "ap-northeast-2"
}

# 1. AWS에 만들어진 내 VPC 가져오기
data "aws_vpc" "aniverse" {
  filter {
    name   = "tag:Name"
    values = ["*aniverse*"]
  }
}

# 2. 내 VPC 안에서 'db' 이름이 들어간 서브넷 ID 자동 가져오기
data "aws_subnets" "db" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.aniverse.id]
  }

  filter {
    name   = "tag:Name"
    values = ["*db*"]
  }
}

data "aws_security_group" "db_sg" {
  filter {
    name   = "tag:Name"
    values = ["*db-sg*", "*rds-sg*", "aniverse-db-sg"]
  }
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.aniverse.id]
  }
}

# 모듈 호출 — private_db_subnet_ids 는 필수 (기본값 없음)
module "my_database_test" {
  source = "../"

  vpc_id                = data.aws_vpc.aniverse.id
  private_db_subnet_ids = data.aws_subnets.db.ids
  db_sg_id              = data.aws_security_group.db_sg.id
  db_password           = "Aniverse1234!"
}

output "test_rds_endpoint" {
  value = module.my_database_test.rds_endpoint
}

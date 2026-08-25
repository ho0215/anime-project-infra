# 1. 임시 프로바이더 설정
provider "aws" {
  region = "ap-northeast-2"
}

# 1. AWS에 만들어진 내 VPC 가져오기
data "aws_vpc" "aniverse" {
  filter {
    name   = "tag:Name"
    values = ["*aniverse*"] # VPC 태그 이름에 aniverse가 들어간 것 자동 검색
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
    values = ["*db*"] # 태그 이름에 db가 포함된 서브넷들 자동 추출
  }
}

data "aws_security_group" "db_sg" {
  filter {
    name   = "tag:Name"
    values = ["aniverse-rds-sg"]
  }
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.aniverse.id]
  }
}

# 2. 내가 만든 모듈 불러오기 (경로 주의: 한 칸 위)
module "my_database_test" {
  source = "../"
  #vpc_id                = data.aws_vpc.aniverse.id
  #private_db_subnet_ids = data.aws_subnets.db.ids
  db_sg_id    = data.aws_security_group.db_sg.id # 추가
  db_password = "aniverse1234"
}

# 3. 결과 확인용 출력
output "test_rds_endpoint" {
  value = module.my_database_test.rds_endpoint
}
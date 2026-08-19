# ── 임시 프로바이더 설정 ────────────────────────────────
provider "aws" {
  region = "ap-northeast-2"
}

# ── VPC 가져오기 ─────────────────────────────────────────
data "aws_vpc" "aniverse" {
  filter {
    name   = "tag:Name"
    values = ["*aniverse*"]
  }
}

# ── 앱 서브넷 가져오기 ──────────────────────────────────
data "aws_subnets" "app" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.aniverse.id]
  }
  filter {
    name   = "tag:Name"
    values = ["*private-app*"]
  }
}

# ── EFS 보안그룹 가져오기 ────────────────────────────────
data "aws_security_group" "efs_sg" {
  filter {
    name   = "tag:Name"
    values = ["*efs-sg*"]
  }
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.aniverse.id]
  }
}

# ── 모듈 호출 ───────────────────────────────────────────
module "my_storage_test" {
  source                 = "../"
  vpc_id                 = data.aws_vpc.aniverse.id
  private_app_subnet_ids = data.aws_subnets.app.ids
  efs_sg_id              = data.aws_security_group.efs_sg.id
}

# ── 결과 확인 ───────────────────────────────────────────
output "test_efs_id" {
  value = module.my_storage_test.efs_id
}

output "test_efs_dns" {
  value = module.my_storage_test.efs_dns_name
}
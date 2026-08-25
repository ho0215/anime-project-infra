provider "aws" {
  region = "ap-northeast-2"
}

# 2. 최신 Amazon Linux 2 AMI 조회 (하드코딩 대신 data source 사용 권장)
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# 3. 내가 만든 nat 모듈 불러오기
module "my_nat_test" {
  source = "../"

  project_name     = "aniverse-test"
  nat_ami          = data.aws_ami.amazon_linux_2.id

  # network test에서 만든 실제 public subnet id로 교체
  public_subnet_id = "subnet-0af31a500a71d9453"

  # security test에서 나온 nat SG output 값으로 교체
  nat_sg_id         = "sg-05893b899d6f1cc9e"
}

# 4. 결과 확인용 출력
output "test_nat_instance_id" {
  value = module.my_nat_test.primary_network_interface_id
}
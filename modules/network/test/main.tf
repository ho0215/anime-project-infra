# 1. 임시 프로바이더 설정
provider "aws" {
  region = "ap-northeast-2"
}

# 2. 내가 만든 모듈 불러오기 (경로 주의: 한 칸 위)
module "my_network_test" {
  source = "../"

  nat_network_interface_id = "eni-08af1b3b54ae0bab4"
}

# 3. 결과 확인용 출력
output "test_vpc_id" {
  value = module.my_network_test.vpc_id
}

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # 주의: 이 부분은 팀원 3이 S3/DynamoDB를 생성한 후 주석을 해제하고 값을 채워야 합니다.
  # backend "s3" {
  #   bucket         = "aniverse-tf-state-bucket"  # 팀원 3이 생성할 S3 버킷 이름
  #   key            = "dev/terraform.tfstate"
  #   region         = "ap-northeast-2"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  # 모든 리소스에 공통으로 들어갈 태그
  default_tags {
    tags = {
      Project     = "Aniverse"
      Environment = "Dev"
      ManagedBy   = "Terraform"
    }
  }
}

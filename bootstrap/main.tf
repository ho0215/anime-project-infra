provider "aws" {
  region = "ap-northeast-2"
}

# S3 버킷 이름은 전 세계 유일.
# "aniverse-tfstate" 는 다른 계정이 이미 사용 중(HeadBucket 403)이므로
# 계정/사용자별로 고유한 이름을 사용한다.
resource "aws_s3_bucket" "tfstate" {
  bucket = "aniverse-tfstate-younju"

  tags = {
    Name = "aniverse-tfstate-younju"
  }
}

resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "terraform_lock" {
  name         = "aniverse-terraform-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name = "aniverse-terraform-lock"
  }
}

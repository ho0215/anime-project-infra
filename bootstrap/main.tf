provider "aws" {
  region = "ap-northeast-2"
}

# S3 버킷 이름은 전 세계 유일.
# 계정 이관(679583587966 → 841535407395)으로 새 버킷 사용 — 옛 버킷은 막힌 계정 소유라 접근 불가.
resource "aws_s3_bucket" "tfstate" {
  bucket = "aniverse-tfstate-sy0227"

  tags = {
    Name = "aniverse-tfstate-sy0227"
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

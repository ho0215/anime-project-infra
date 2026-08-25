provider "aws" {
  region = "ap-northeast-2"
}

# ── tfstate 저장용 S3 ──────────────────────────────────
resource "aws_s3_bucket" "tfstate" {
  bucket = "aniverse-tfstate"

  tags = {
    Name = "aniverse-tfstate"
  }
}

# 버전 관리 (실수로 덮어써도 복구 가능)
resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 퍼블릭 접근 완전 차단 (tfstate는 절대 공개 X)
resource "aws_s3_bucket_public_access_block" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ── 잠금용 DynamoDB ────────────────────────────────────
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
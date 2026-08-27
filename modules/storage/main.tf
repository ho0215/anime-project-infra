# ── EFS 파일시스템 ──────────────────────────────────────
resource "aws_efs_file_system" "main" {
  tags = {
    Name = "${var.project_name}-efs"
  }
}
# ── EFS 마운트 타겟 (가용영역 2개) ─────────────────────
resource "aws_efs_mount_target" "main" {
  count           = length(var.private_app_subnet_ids)
  file_system_id  = aws_efs_file_system.main.id
  subnet_id       = var.private_app_subnet_ids[count.index]
  security_groups = [var.efs_sg_id]
}
# ── S3 버킷 (정적 파일용) ───────────────────────────────
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
resource "aws_s3_bucket" "static" {
  bucket        = "${var.bucket_name}-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}"
  force_destroy = true

  tags = {
    Name = var.bucket_name
  }
}
# ── S3 퍼블릭 접근 허용 ─────────────────────────────────
resource "aws_s3_bucket_public_access_block" "static" {
  bucket = aws_s3_bucket.static.id
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = false
  restrict_public_buckets = false
}
# ACL 비활성 — 버킷 정책으로만 공개 읽기
resource "aws_s3_bucket_ownership_controls" "static" {
  bucket = aws_s3_bucket.static.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}
resource "aws_s3_bucket_cors_configuration" "static" {
  bucket = aws_s3_bucket.static.id
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}
# ── S3 버킷 정책 (읽기 허용) ────────────────────────────
resource "aws_s3_bucket_policy" "static" {
  bucket = aws_s3_bucket.static.id
  depends_on = [
    aws_s3_bucket_public_access_block.static,
    aws_s3_bucket_ownership_controls.static,
  ]
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.static.arn}/*"
      }
    ]
  })
}
# ── S3 수명주기 정책 ─────────────────────────────────────
resource "aws_s3_bucket_lifecycle_configuration" "static" {
  bucket = aws_s3_bucket.static.id
  rule {
    id     = "delete-old-media"
    status = "Enabled"
    expiration {
      days = 90
    }
  }
}

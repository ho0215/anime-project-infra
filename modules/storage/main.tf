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
resource "aws_s3_bucket" "static" {
  bucket = var.bucket_name

  tags = {
    Name = var.bucket_name
  }
}

# ── S3 퍼블릭 접근 허용 ─────────────────────────────────
resource "aws_s3_bucket_public_access_block" "static" {
  bucket = aws_s3_bucket.static.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# ── S3 버킷 정책 (읽기 허용) ────────────────────────────
resource "aws_s3_bucket_policy" "static" {
  bucket = aws_s3_bucket.static.id

  depends_on = [aws_s3_bucket_public_access_block.static]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.static.arn}/*"
      }
    ]
  })
}
# ── EFS 보안그룹 ────────────────────────────────────────
resource "aws_security_group" "efs" {
  name   = "${var.project_name}-efs-sg"
  vpc_id = var.vpc_id

  # Django 서버에서만 NFS(2049) 허용
  ingress {
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    cidr_blocks = var.private_app_subnet_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-efs-sg"
  }
}

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
  security_groups = [aws_security_group.efs.id]
}
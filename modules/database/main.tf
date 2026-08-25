resource "random_id" "final_snapshot_suffix" {
  byte_length = 4
}

# ── DB 서브넷 그룹 (Terraform이 직접 생성) ────────────────
# AWS에 같은 이름(aniverse-db-subnet-group)이 이미 있으면:
#   terraform import module.database.aws_db_subnet_group.main aniverse-db-subnet-group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = var.private_db_subnet_ids

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# ── RDS 영속성 옵션 (literal locals — var 쓰면 IDE 오탐 반복) ─
# 스냅샷 복원 시 GitHub Actions 가 아래 두 줄만 덮어쓴다.
locals {
  db_snapshot_identifier       = ""
  restore_from_latest_snapshot = false
  backup_retention_period      = 7
  deletion_protection          = false

  snapshot_trimmed  = trimspace(local.db_snapshot_identifier)
  explicit_snapshot = local.snapshot_trimmed != "" ? local.snapshot_trimmed : null
}

# ── 최신 manual 스냅샷 조회 (옵션, 기본 OFF) ─────────────
data "aws_db_snapshot" "latest" {
  count = local.restore_from_latest_snapshot && local.explicit_snapshot == null ? 1 : 0

  most_recent            = true
  db_instance_identifier = "${var.project_name}-rds"
  snapshot_type          = "manual"
}

locals {
  latest_snapshot       = try(data.aws_db_snapshot.latest[0].id, null)
  effective_snapshot_id = local.explicit_snapshot != null ? local.explicit_snapshot : local.latest_snapshot
  is_restore            = local.effective_snapshot_id != null
}

# ── RDS 파라미터 그룹 ────────────────────────────────────
resource "aws_db_parameter_group" "main" {
  name   = "${var.project_name}-db-parameter-group"
  family = "mariadb10.11"

  parameter {
    name  = "time_zone"
    value = "Asia/Seoul"
  }

  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }

  parameter {
    name  = "collation_server"
    value = "utf8mb4_unicode_ci"
  }

  tags = {
    Name = "${var.project_name}-db-parameter-group"
  }
}

# ── RDS (MariaDB) ────────────────────────────────────────
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-rds"
  engine         = "mariadb"
  engine_version = "10.11"
  instance_class = "db.t3.micro"
  storage_type   = "gp2"

  # 신규 생성 시에만 지정. 스냅샷 복원 시에는 스냅샷 값 사용.
  allocated_storage = local.is_restore ? null : 20
  db_name           = local.is_restore ? null : var.db_name
  username          = local.is_restore ? null : var.db_username
  password          = var.db_password

  snapshot_identifier    = local.effective_snapshot_id
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.db_sg_id]
  parameter_group_name   = aws_db_parameter_group.main.name

  multi_az            = false
  publicly_accessible = false

  backup_retention_period   = local.backup_retention_period
  backup_window             = "18:00-19:00"
  maintenance_window        = "sun:19:00-sun:20:00"
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.project_name}-rds-final-${random_id.final_snapshot_suffix.hex}"
  copy_tags_to_snapshot     = true
  deletion_protection       = local.deletion_protection

  lifecycle {
    ignore_changes = [
      snapshot_identifier,
      final_snapshot_identifier,
      engine_version,
    ]
  }

  tags = {
    Name = "${var.project_name}-rds"
  }
}

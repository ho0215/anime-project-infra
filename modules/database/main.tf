resource "random_id" "final_snapshot_suffix" {
  byte_length = 4
}

# ── DB 서브넷 그룹 (Terraform이 직접 생성) ────────────────
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = var.private_db_subnet_ids

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# ── 최신 manual 스냅샷 조회 (옵션) ───────────────────────
# 주의: 스냅샷이 하나도 없으면 data source 가 실패하므로
# restore_from_latest_snapshot 은 스냅샷이 존재할 때만 true 로 켠다.
data "aws_db_snapshot" "latest" {
  count = var.restore_from_latest_snapshot && var.db_snapshot_identifier == "" ? 1 : 0

  most_recent            = true
  db_instance_identifier = "${var.project_name}-rds"
  snapshot_type          = "manual"
}

locals {
  effective_snapshot_id = var.db_snapshot_identifier != "" ? var.db_snapshot_identifier : (
    try(data.aws_db_snapshot.latest[0].id, null)
  )
  is_restore = local.effective_snapshot_id != null
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

  # 스냅샷 복원 시 allocated_storage/db_name 은 스냅샷 기준
  allocated_storage = local.is_restore ? null : 20
  db_name           = local.is_restore ? null : var.db_name
  username          = var.db_username
  password          = var.db_password

  snapshot_identifier    = local.effective_snapshot_id
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.db_sg_id]
  parameter_group_name   = aws_db_parameter_group.main.name

  multi_az            = false
  publicly_accessible = false

  # 영속성: 자동 백업 + destroy 시 최종 스냅샷 보존
  backup_retention_period   = var.backup_retention_period
  backup_window             = "18:00-19:00"
  maintenance_window        = "sun:19:00-sun:20:00"
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.project_name}-rds-final-${random_id.final_snapshot_suffix.hex}"
  copy_tags_to_snapshot     = true
  deletion_protection       = var.deletion_protection

  # 최초 생성 시에만 스냅샷/파이널 식별자를 고정해 불필요한 재생성 방지
  lifecycle {
    ignore_changes = [snapshot_identifier, final_snapshot_identifier]
  }

  tags = {
    Name = "${var.project_name}-rds"
  }
}

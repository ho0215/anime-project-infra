resource "random_id" "final_snapshot_suffix" {
  byte_length = 4
}

# ── DB 서브넷 그룹 (Terraform이 직접 생성) ────────────────
# 주의: AWS에 같은 이름(aniverse-db-subnet-group)이 이미 있으면
#       최초 apply 전에 import 하거나 기존 그룹을 삭제해야 합니다.
#   terraform import module.database.aws_db_subnet_group.main aniverse-db-subnet-group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = var.private_db_subnet_ids

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# ── 최신 manual 스냅샷 조회 (옵션, 기본 OFF) ─────────────
# restore_from_latest_snapshot=true 이고 스냅샷이 0개면 plan/apply 가 실패합니다.
data "aws_db_snapshot" "latest" {
  count = var.restore_from_latest_snapshot && var.db_snapshot_identifier == null ? 1 : 0

  most_recent            = true
  db_instance_identifier = "${var.project_name}-rds"
  snapshot_type          = "manual"
}

locals {
  # 우선순위: 명시적 스냅샷 ID > (옵션) 최신 manual 스냅샷 > 신규 생성
  # coalesce 는 인자가 모두 null/"" 이면 에러 → try 로 null 폴백
  effective_snapshot_id = try(
    coalesce(
      var.db_snapshot_identifier,
      try(data.aws_db_snapshot.latest[0].id, null),
    ),
    null,
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
# 신규 생성과 스냅샷 복원에서 필수 인자가 다릅니다.
# - 신규: allocated_storage / db_name / username 필수
# - 복원: 위 값들은 스냅샷에서 상속 (지정하면 충돌할 수 있음)
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-rds"
  engine         = "mariadb"
  engine_version = "10.11"
  instance_class = "db.t3.micro"
  storage_type   = "gp2"

  # 복원 시에는 null 을 넘겨 "미설정"으로 처리 (provider가 omit)
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

  backup_retention_period   = var.backup_retention_period
  backup_window             = "18:00-19:00"
  maintenance_window        = "sun:19:00-sun:20:00"
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.project_name}-rds-final-${random_id.final_snapshot_suffix.hex}"
  copy_tags_to_snapshot     = true
  deletion_protection       = var.deletion_protection

  lifecycle {
    ignore_changes = [
      snapshot_identifier,
      final_snapshot_identifier,
      # 복원 직후 provider가 스냅샷 값을 읽으면 drift 로 보일 수 있어 고정
      engine_version,
    ]
  }

  tags = {
    Name = "${var.project_name}-rds"
  }
}

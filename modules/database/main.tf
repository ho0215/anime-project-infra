# ── DB 서브넷 그룹 (서이꺼 참조) ────────────────────────
data "aws_db_subnet_group" "main" {
  name = "${var.project_name}-db-subnet-group"
}

# ── RDS 파라미터 그룹 ────────────────────────────────────
resource "aws_db_parameter_group" "main" {
  name   = "${var.project_name}-db-parameter-group"
  family = "mariadb10.11"

  # 한국 시간대 설정
  parameter {
    name  = "time_zone"
    value = "Asia/Seoul"
  }

  # 한글 + 이모지 저장 가능하게
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
  identifier        = "${var.project_name}-rds"
  engine            = "mariadb"
  engine_version    = "10.11"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = data.aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.db_sg_id]
  parameter_group_name   = aws_db_parameter_group.main.name

  # 비용 절감
  multi_az                = false
  backup_retention_period = 0
  skip_final_snapshot     = true
  deletion_protection     = false

  tags = {
    Name = "${var.project_name}-rds"
  }
}
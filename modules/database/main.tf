# ── DB 서브넷 그룹 ──────────────────────────────────────
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = var.private_db_subnet_ids

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# ── RDS (MariaDB) ───────────────────────────────────────
resource "aws_db_instance" "main" {
  identifier        = "${var.project_name}-rds"
  engine            = "mariadb"
  engine_version    = "10.11"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.db_sg_id]  # security 모듈꺼 받아옴

  multi_az            = true
  skip_final_snapshot = true

  tags = {
    Name = "${var.project_name}-rds"
  }
}
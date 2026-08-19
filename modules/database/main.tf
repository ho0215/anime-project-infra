# ── DB 서브넷 그룹 ──────────────────────────────────────
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = var.private_db_subnet_ids   # 박서이꺼에서 받아옴

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# ── RDS 보안그룹 ────────────────────────────────────────
resource "aws_security_group" "rds" {
  name   = "${var.project_name}-rds-sg"
  vpc_id = var.vpc_id

  # Django(프라이빗 앱 서브넷)에서만 3306 허용
  ingress {
    from_port   = 3306
    to_port     = 3306
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
    Name = "${var.project_name}-rds-sg"
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
  vpc_security_group_ids = [aws_security_group.rds.id]

  multi_az            = true    # 가용영역 2개 = 고가용성
  skip_final_snapshot = true    # 실습용이라 삭제 시 스냅샷 생략

  tags = {
    Name = "${var.project_name}-rds"
  }
}
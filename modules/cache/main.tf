# Django Channels(웹소켓) 채널 레이어용 Redis. 단일 노드 — HA/replication 없음,
# 팀 프로젝트 스케일에 맞춰 비용 최소화(운영 DB 아니라 캐시/채널 레이어라 데이터
# 유실 허용 가능). 필요해지면 aws_elasticache_replication_group으로 전환.

resource "aws_security_group" "redis" {
  name        = "${var.project_name}-redis-sg"
  description = "Allow Redis(6379) from EKS pod subnets only"
  vpc_id      = var.vpc_id

  ingress {
    description = "Redis from private-app subnets (EKS pods)"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-redis-sg" }
}

resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.project_name}-redis-subnet-group"
  subnet_ids = var.private_db_subnet_ids
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${var.project_name}-redis"
  engine               = "redis"
  engine_version       = "7.1"
  node_type            = var.node_type
  num_cache_nodes      = 1
  port                 = 6379
  parameter_group_name = "default.redis7"

  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]

  tags = { Name = "${var.project_name}-redis" }
}

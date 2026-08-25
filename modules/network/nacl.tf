# nacl.tf

resource "aws_network_acl" "private_db" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.private_db[*].id

  tags = {
    Name = "${var.project_name}-db-nacl"
  }
}

locals {
  db_inbound_mysql_rules = {
    for idx, cidr in var.private_app_subnet_cidrs :
    cidr => idx + 100
  }

  db_inbound_redis_rules = {
    for idx, cidr in var.private_app_subnet_cidrs :
    cidr => idx + 200
  }
}

resource "aws_network_acl_rule" "db_inbound_mysql" {
  for_each = local.db_inbound_mysql_rules

  network_acl_id = aws_network_acl.private_db.id
  rule_number    = each.value
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = each.key # App 서브넷 대역, variables.tf에 정의
  from_port      = 3306
  to_port        = 3306
}

resource "aws_network_acl_rule" "db_inbound_redis" {
  for_each = local.db_inbound_redis_rules

  network_acl_id = aws_network_acl.private_db.id
  rule_number    = each.value
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = each.key
  from_port      = 6379
  to_port        = 6379
}

# 응답 트래픽용 에페메럴 포트 허용 (VPC 전체 대역 기준)
# (현재는 사용 안 하지만 팀원이 모니터링 기능 도입 예정이라 유지)
resource "aws_network_acl_rule" "db_inbound_ephemeral" {
  network_acl_id = aws_network_acl.private_db.id
  rule_number    = 300
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = var.vpc_cidr
  from_port      = 1024
  to_port        = 65535
}

# App 서브넷으로의 응답 트래픽(에페메럴 포트) 허용
resource "aws_network_acl_rule" "db_outbound_ephemeral" {
  network_acl_id = aws_network_acl.private_db.id
  rule_number    = 100
  egress         = true
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = var.private_app_subnet_cidrs[0] # 또는 여러 대역이면 규칙을 여러 개로 분리
  from_port      = 1024
  to_port        = 65535
}
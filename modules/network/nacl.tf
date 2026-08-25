# nacl.tf — DB 서브넷 전용 NACL (stateless: 왕복 규칙을 모두 열어야 함)

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
    cidr => 100 + idx
  }

  db_inbound_redis_rules = {
    for idx, cidr in var.private_app_subnet_cidrs :
    cidr => 200 + idx
  }

  # 응답(에페메럴) outbound 도 모든 app 서브넷에 열어줘야 함.
  # 예전에는 [0] 만 허용해서 2번째 AZ EC2 → RDS 가 timeout(110) 났음.
  db_outbound_ephemeral_rules = {
    for idx, cidr in var.private_app_subnet_cidrs :
    cidr => 100 + idx
  }
}

resource "aws_network_acl_rule" "db_inbound_mysql" {
  for_each = local.db_inbound_mysql_rules

  network_acl_id = aws_network_acl.private_db.id
  rule_number    = each.value
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = each.key
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

# 클라이언트 → DB 접속 시 쓰는 ephemeral 포트 응답용 (inbound to DB from VPC)
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

# DB → App 응답 트래픽 (모든 private app 서브넷)
resource "aws_network_acl_rule" "db_outbound_ephemeral" {
  for_each = local.db_outbound_ephemeral_rules

  network_acl_id = aws_network_acl.private_db.id
  rule_number    = each.value
  egress         = true
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = each.key
  from_port      = 1024
  to_port        = 65535
}

# VPC 내부 기타 egress 여유분
resource "aws_network_acl_rule" "db_outbound_vpc_all" {
  network_acl_id = aws_network_acl.private_db.id
  rule_number    = 300
  egress         = true
  protocol       = "-1"
  rule_action    = "allow"
  cidr_block     = var.vpc_cidr
  from_port      = 0
  to_port        = 0
}

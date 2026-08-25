# VPC Interface Endpoints for SSM Session Manager
# Private subnet EC2 can talk to SSM without depending on the NAT instance.

data "aws_region" "current" {}

resource "aws_security_group" "vpce" {
  name        = "${var.project_name}-vpce-sg"
  description = "Allow HTTPS from VPC to interface VPC endpoints (SSM)"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTPS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-vpce-sg"
  }
}

locals {
  ssm_services = [
    "ssm",
    "ssmmessages",
    "ec2messages",
  ]
}

resource "aws_vpc_endpoint" "ssm" {
  for_each = toset(local.ssm_services)

  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.${each.value}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.private_app_subnet_ids
  security_group_ids  = [aws_security_group.vpce.id]
  private_dns_enabled = true

  tags = {
    Name = "${var.project_name}-vpce-${each.value}"
  }
}

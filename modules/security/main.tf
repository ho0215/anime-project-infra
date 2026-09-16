# NAT SG only — EKS 노드는 클러스터/노드 SG 사용, Ingress ALB SG 는 LB Controller 가 관리

resource "aws_security_group" "nat" {
  name        = "${var.project_name}-nat-sg"
  description = "Allow traffic from private subnets for NAT routing"
  vpc_id      = var.vpc_id

  ingress {
    description = "All traffic from private app/db subnet CIDRs"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = concat(var.private_app_subnet_cidrs, var.private_db_subnet_cidrs)
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-nat-sg" }
}

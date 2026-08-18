# ── VPC ──────────────────────────────────────────────
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# ── Internet Gateway (퍼블릭 서브넷용) ─────────────────
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# ── 퍼블릭 서브넷 ────────────────────────
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-${count.index + 1}"
    Tier = "public"
  }
}

# ── 프라이빗 앱 서브넷 (Django/Nginx EC2 배치) ──────────
resource "aws_subnet" "private_app" {
  count             = length(var.private_app_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_app_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.project_name}-private-app-${count.index + 1}"
    Tier = "private-app"
  }
}

# ── 프라이빗 DB 서브넷 (MariaDB, Redis 배치) ────────────
resource "aws_subnet" "private_db" {
  count             = length(var.private_db_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_db_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.project_name}-private-db-${count.index + 1}"
    Tier = "private-db"
  }
}

# ── NAT 인스턴스 구성 ────────────────────────
resource "aws_instance" "nat" {
  ami                    = "ami-0cde067c44daf99fc"  # Amazon Linux 2, 서울 리전 최신 AMI ID 확인 필요
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public[0].id
  #vpc_security_group_ids = [aws_security_group.nat.id] 추후 보안그룹에 추가가
  source_dest_check      = false

  user_data = <<-EOF
    #!/bin/bash
    # IP 포워딩 활성화
    echo 1 > /proc/sys/net/ipv4/ip_forward
    sysctl -w net.ipv4.ip_forward=1

    # NAT(Masquerade) 설정
    /sbin/iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
    /sbin/iptables -F FORWARD

    # iptables 규칙 영구 저장 (재부팅해도 유지)
    service iptables save
  EOF

  tags = {
    Name = "${var.project_name}-nat-instance"
  }
}

# ── 라우팅 테이블: 퍼블릭 ───────────────────────────────
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# ── 라우팅 테이블: 프라이빗 (NAT 경유) ──────────────────
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    network_interface_id = aws_instance.nat.primary_network_interface_id
  }

  tags = {
    Name = "${var.project_name}-private-rt"
  }
}

resource "aws_route_table_association" "private_app" {
  count          = length(aws_subnet.private_app)
  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_db" {
  count          = length(aws_subnet.private_db)
  subnet_id      = aws_subnet.private_db[count.index].id
  route_table_id = aws_route_table.private.id
}

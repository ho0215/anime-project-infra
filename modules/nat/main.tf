resource "aws_instance" "nat" {
  ami                    = var.nat_ami
  instance_type          = "t3.micro"
  subnet_id              = var.public_subnet_id
  vpc_security_group_ids = [var.nat_sg_id]
  source_dest_check      = false
  iam_instance_profile = aws_iam_instance_profile.nat_profile.name

  iam_instance_profile = aws_iam_instance_profile.nat_profile.name

  user_data = <<-EOF
    #!/bin/bash
    echo 1 > /proc/sys/net/ipv4/ip_forward
    sysctl -w net.ipv4.ip_forward=1

    # sysctl 설정을 영구 반영 (재부팅 시에도 유지)
    echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf

    IFACE=$(ip -o -4 route show to default | awk '{print $5}')
    /sbin/iptables -t nat -A POSTROUTING -o $IFACE -j MASQUERADE
    /sbin/iptables -F FORWARD

    yum install -y iptables-services
    service iptables save

    # 재부팅 시 iptables 규칙 자동 복원되도록 서비스 활성화
    systemctl enable iptables
    systemctl start iptables
  EOF

  tags = {
    Name = "${var.project_name}-nat-instance"
  }
}

# ── SSM 접속용 IAM Role ─────────────────────
resource "aws_iam_role" "nat_ssm_role" {
  name = "${var.project_name}-nat-ssm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  tags = {
    Name = "${var.project_name}-nat-ssm-role"
  }
}

resource "aws_iam_role_policy_attachment" "nat_ssm_core" {
  role       = aws_iam_role.nat_ssm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "nat_profile" {
  name = "${var.project_name}-nat-instance-profile"
  role = aws_iam_role.nat_ssm_role.name
}
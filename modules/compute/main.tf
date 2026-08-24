# ── Application Load Balancer (퍼블릭) ─────────────────
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_sg_id]
  subnets            = var.public_subnet_ids
}

# ── ALB 타겟 그룹 및 리스너 ──────────────────────────
resource "aws_lb_target_group" "app" {
  name     = "${var.project_name}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    path                = "/health/"
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# ── 우분투 22.04 LTS 최신 AMI 조회 ────────────────────
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical 공식 계정

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ── Launch Template (프라이빗 앱 인스턴스용) ────────────
resource "aws_launch_template" "app" {
  name_prefix   = "${var.project_name}-app-template"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  vpc_security_group_ids = [var.app_sg_id]

  # IAM 역할 부여 (SSM 및 CodeDeploy 권한 필수)
  iam_instance_profile {
    name = aws_iam_instance_profile.app_profile.name
  }

  # 인스턴스 부팅 시 CodeDeploy Agent 자동 설치
  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -e

    # 네트워크 초기화 대기
    sleep 10

    apt-get update -y
    apt-get install -y ruby-full wget

    cd /tmp
    wget https://aws-codedeploy-ap-northeast-2.s3.ap-northeast-2.amazonaws.com/latest/install
    chmod +x ./install
    ./install auto

    systemctl enable codedeploy-agent
    systemctl start codedeploy-agent
  EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-app-instance"
    }
  }
}

# ── Bastion Host (퍼블릭 서브넷) ──────────────────────
resource "aws_instance" "bastion" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t3.micro"
  subnet_id                   = var.public_subnet_ids[0]
  associate_public_ip_address = true
  vpc_security_group_ids      = aniverse-bastion-sg
  iam_instance_profile        = aws_iam_instance_profile.app_profile.name

  tags = {
    Name = "${var.project_name}-bastion"
  }
}

# ── Auto Scaling Group (프라이빗 앱 서브넷) ───────────
resource "aws_autoscaling_group" "app" {
  name                = "${var.project_name}-asg"
  desired_capacity    = 2
  max_size            = 4
  min_size            = 2
  vpc_zone_identifier = var.private_app_subnet_ids
  target_group_arns   = [aws_lb_target_group.app.arn]

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }
}
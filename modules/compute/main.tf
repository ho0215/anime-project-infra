# ── 1. Launch Template: "이런 서버를 만들어줘"라는 설계도 ──
resource "aws_launch_template" "app" {
  name_prefix   = "app-lt-"
  image_id      = var.ami_id           # 어떤 OS 이미지 쓸지
  instance_type = var.instance_type    # 서버 사양 (예: t3.micro)

  network_interfaces {
    associate_public_ip_address = false   # 프라이빗이라 공인IP 없음
    security_groups             = [var.ec2_sg_id]  # 박서이님이 만든 방화벽 규칙
  }

  # EC2가 켜질 때 자동 실행되는 설치 스크립트
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    efs_id = var.efs_id
  }))

  tag_specifications {
    resource_type = "instance"
    tags = { Name = "app-instance" }
  }
}

# ── 2. ALB: 사용자 요청을 받는 문 ──
resource "aws_lb" "app" {
  name               = "app-alb"
  internal           = false                    # 외부(인터넷)에 열려있음
  load_balancer_type = "application"
  security_groups    = [var.alb_sg_id]
  subnets            = var.public_subnet_ids     # 퍼블릭 서브넷에 위치
}

# ── 3. Target Group: ALB가 요청 보낼 대상 명단 ──
resource "aws_lb_target_group" "app" {
  name     = "app-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    path                = "/"     # 이 주소로 서버가 살아있는지 확인
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }
}

# ── 4. Listener: ALB가 어느 포트로 들어온 요청을 어디로 보낼지 ──
resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# ── 5. ASG: EC2 서버 개수를 자동 관리 ──
resource "aws_autoscaling_group" "app" {
  name                = "app-asg"
  desired_capacity    = var.desired_capacity   # 평소 유지할 서버 수
  min_size            = var.min_size           # 최소
  max_size            = var.max_size           # 최대
  vpc_zone_identifier = var.private_subnet_ids # 프라이빗 서브넷에 서버 배치

  target_group_arns = [aws_lb_target_group.app.arn]  # ALB와 연결

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "app-asg-instance"
    propagate_at_launch = true
  }
}

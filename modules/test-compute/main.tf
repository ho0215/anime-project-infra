provider "aws" {
  region = "ap-northeast-2"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# IAM 역할 생성 (EC2가 SSM을 쓸 수 있게 허용)
resource "aws_iam_role" "ec2_ssm_role" {
  name = "test-ec2-ssm-role-v2"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# SSM 관련 권한 붙이기
resource "aws_iam_role_policy_attachment" "ssm_policy" {
  role       = aws_iam_role.ec2_ssm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# EC2가 이 역할을 실제로 쓸 수 있게 하는 "인스턴스 프로필"
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "test-ec2-ssm-profile-v2"
  role = aws_iam_role.ec2_ssm_role.name
}

# ── Launch Template: "이런 서버를 만들어줘"라는 설계도 ──
resource "aws_launch_template" "app" {
  name_prefix   = "test-app-lt-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  user_data     = base64encode(file("${path.module}/user_data.sh"))

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2_profile.name
  }

  network_interfaces {
    associate_public_ip_address = false
    security_groups              = ["sg-0197912fe68200772"]
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "test-app-instance"
    }
  }
}

# ── ASG: Launch Template을 보고 EC2를 자동으로 관리 ──
resource "aws_autoscaling_group" "app" {
  name                = "test-app-asg"
  desired_capacity    = 1
  min_size            = 1
  max_size            = 1
  vpc_zone_identifier = ["subnet-04be3ea857d4e85ef"]

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "test-app-asg-instance"
    propagate_at_launch = true
  }
}

output "asg_name" {
  value = aws_autoscaling_group.app.name
}

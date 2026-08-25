# ── 우분투 22.04 LTS 최신 AMI 조회 ────────────────────
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

# ── Launch Template (프라이빗 앱 인스턴스용) ────────────
resource "aws_launch_template" "app" {
  name_prefix   = "${var.project_name}-app-template"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  vpc_security_group_ids = [var.app_sg_id]

  iam_instance_profile {
    name = aws_iam_instance_profile.app_profile.name
  }

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    efs_dns_name = var.efs_dns_name
    db_host      = var.db_host
    db_port      = var.db_port
    db_name      = var.db_name
    db_username  = var.db_username
    # .env 단일 인용부호 이스케이프
    db_password        = replace(var.db_password, "'", "'\"'\"'")
    static_bucket_name = var.static_bucket_name
    aws_region         = data.aws_region.current.name
    django_secret_key  = replace(var.django_secret_key, "'", "'\"'\"'")
    gemini_api_key     = replace(var.gemini_api_key, "'", "'\"'\"'")
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name    = "${var.project_name}-app-instance"
      Project = var.project_name
    }
  }
}

# ── IAM: SSM + CodeDeploy + S3 ─────────────────────────
resource "aws_iam_role" "app_role" {
  name = "${var.project_name}-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "app_ssm" {
  role       = aws_iam_role.app_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "app_codedeploy" {
  role       = aws_iam_role.app_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforAWSCodeDeploy"
}

resource "aws_iam_role_policy" "app_s3" {
  name = "${var.project_name}-app-s3"
  role = aws_iam_role.app_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "StaticBucket"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
        Resource = [
          var.static_bucket_arn,
          "${var.static_bucket_arn}/*",
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "app_profile" {
  name = "${var.project_name}-app-instance-profile"
  role = aws_iam_role.app_role.name
}

# ── Auto Scaling Group (프라이빗 앱 서브넷) ───────────
resource "aws_autoscaling_group" "app" {
  name                = "${var.project_name}-asg"
  desired_capacity    = var.asg_desired_capacity
  max_size            = var.asg_max_size
  min_size            = var.asg_min_size
  vpc_zone_identifier = var.private_app_subnet_ids
  target_group_arns   = [var.target_group_arn]
  health_check_type   = "ELB"
  # user_data 가 임시 /health/ 를 띄우고, CodeDeploy 가 앱을 설치할 시간을 확보
  health_check_grace_period = 900

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-app-instance"
    propagate_at_launch = true
  }

  lifecycle {
    create_before_destroy = true
  }
}

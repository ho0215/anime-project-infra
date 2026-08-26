data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# 1. 배포용 S3 버킷 (계정/리전 접미사로 전역 유일성 보장)
resource "aws_s3_bucket" "deploy_bucket" {
  bucket        = "${var.project_name}-deploy-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}"
  force_destroy = true

  tags = {
    Name = "${var.project_name}-deploy-bucket"
  }
}

resource "aws_s3_bucket_public_access_block" "deploy" {
  bucket = aws_s3_bucket.deploy_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "deploy" {
  bucket = aws_s3_bucket.deploy_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 2. CodeDeploy 서비스용 IAM 역할
resource "aws_iam_role" "codedeploy_role" {
  name = "${var.project_name}-codedeploy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "codedeploy.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "codedeploy_policy" {
  role       = aws_iam_role.codedeploy_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole"
}

# 3. EC2 앱 역할에 배포 버킷 읽기 권한 부여 (순환 참조 방지: cicd → compute role)
resource "aws_iam_role_policy" "app_deploy_bucket" {
  name = "${var.project_name}-deploy-bucket-read"
  role = var.app_role_name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:GetObjectVersion", "s3:ListBucket"]
        Resource = [
          aws_s3_bucket.deploy_bucket.arn,
          "${aws_s3_bucket.deploy_bucket.arn}/*",
        ]
      }
    ]
  })
}

# 4. CodeDeploy 애플리케이션
resource "aws_codedeploy_app" "app" {
  compute_platform = "Server"
  name             = var.codedeploy_app_name
}

# 5. CodeDeploy 배포 그룹 (앱 저장소 deploy.yml 과 이름 일치)
resource "aws_codedeploy_deployment_group" "dg" {
  app_name              = aws_codedeploy_app.app.name
  deployment_group_name = var.codedeploy_group_name
  service_role_arn      = aws_iam_role.codedeploy_role.arn

  autoscaling_groups = [var.asg_name]

  # 소규모 ASG(2대)에서 1대 실패 시 나머지가 Skip 되는 것을 줄임
  deployment_config_name = "CodeDeployDefault.AllAtOnce"

  # 첫 배포 / 에이전트 이슈 시 ApplicationStop 실패로 전체가 죽지 않게
  ignore_application_stop_failures = true

  deployment_style {
    deployment_option = "WITHOUT_TRAFFIC_CONTROL"
    deployment_type   = "IN_PLACE"
  }

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE"]
  }
}

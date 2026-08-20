# 1. 배포용 S3 버킷 (이름 중복 방지를 위해 random_id 사용)
resource "random_id" "bucket_id" {
  byte_length = 4
}

resource "aws_s3_bucket" "deploy_bucket" {
  bucket        = "${var.project_name}-deploy-bucket-${random_id.bucket_id.hex}"
  force_destroy = true

  tags = {
    Name = "${var.project_name}-deploy-bucket"
  }
}

# 2. CodeDeploy 서비스용 IAM 역할 (AWS가 CodeDeploy를 대신 실행할 권한)
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

# 3. CodeDeploy 애플리케이션
resource "aws_codedeploy_app" "app" {
  compute_platform = "Server"
  name             = "${var.project_name}-app"
}

# 4. CodeDeploy 배포 그룹 (ASG 연동 및 롤백 설정)
resource "aws_codedeploy_deployment_group" "dg" {
  app_name              = aws_codedeploy_app.app.name
  deployment_group_name = "${var.project_name}-dg"
  service_role_arn      = aws_iam_role.codedeploy_role.arn

  # 팀원 2가 만든 ASG에 새로운 코드를 자동으로 배포하도록 연동
  autoscaling_groups = [var.asg_name]

  # 배포 실패 시 자동으로 이전 정상 버전으로 롤백하는 안전장치
  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE"]
  }
}

variable "project_name" {
  description = "프로젝트 이름 (리소스 네이밍용)"
  type        = string
  default     = "aniverse"
}

variable "asg_name" {
  description = "Auto Scaling Group 이름"
  type        = string
}

variable "app_role_name" {
  description = "EC2 앱 인스턴스 IAM 역할 이름 (배포 버킷 읽기 권한 부착용)"
  type        = string
}

variable "codedeploy_app_name" {
  type    = string
  default = "aniverse-app"
}

variable "codedeploy_group_name" {
  # anime-project/.github/workflows/deploy.yml 과 반드시 일치
  type    = string
  default = "aniverse-deployment-group"
}

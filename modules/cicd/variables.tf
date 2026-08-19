variable "project_name" {
  description = "프로젝트 이름 (리소스 네이밍용)"
  type        = string
  default     = "aniverse"
}

variable "asg_name" {
  description = "팀원 2(컴퓨팅 모듈)가 생성할 Auto Scaling Group의 이름"
  type        = string
}

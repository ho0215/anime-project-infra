variable "project_name" {
  description = "프로젝트 이름"
  type        = string
}

variable "alert_email" {
  description = "ho021524@gmail.com"
  type        = string
}

variable "asg_name" {
  description = "팀원 2가 생성할 Auto Scaling Group의 이름"
  type        = string
}

variable "alb_arn_suffix" {
  description = "팀원 2가 생성할 ALB의 식별자(ARN Suffix)"
  type        = string
}
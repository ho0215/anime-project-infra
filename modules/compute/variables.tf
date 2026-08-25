variable "name_prefix" {
  type        = string
  description = "리소스 이름 접두사"
  default     = "app"
}

variable "ami_id" {
  type        = string
  description = "AMI ID. 빈 값이면 최신 Amazon Linux 2023 자동 조회"
  default     = ""
}

variable "instance_type" {
  type        = string
  default     = "t3.micro"
}

variable "ec2_sg_id" {
  type        = string
  description = "EC2에 붙일 보안그룹 ID"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "ASG가 EC2를 띄울 프라이빗 서브넷들"
}

variable "efs_id" {
  type        = string
  description = "마운트할 EFS 파일시스템 ID"
}

variable "target_group_arn" {
  type        = string
  description = "alb 모듈에서 생성된 Target Group ARN"
}

variable "desired_capacity" {
  type    = number
  default = 1
}

variable "min_size" {
  type    = number
  default = 1
}

variable "max_size" {
  type    = number
  default = 2
}
variable "vpc_id" {
  description = "박서이님 네트워크 모듈에서 받는 VPC ID"
}

variable "public_subnet_ids" {
  description = "ALB가 위치할 퍼블릭 서브넷 목록 (박서이님)"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "EC2가 위치할 프라이빗 서브넷 목록 (박서이님)"
  type        = list(string)
}

variable "ec2_sg_id" {
  description = "EC2용 보안그룹 ID (박서이님)"
}

variable "alb_sg_id" {
  description = "ALB용 보안그룹 ID (박서이님)"
}

variable "efs_id" {
  description = "공유 파일저장소 ID (김윤주님)"
}

variable "ami_id" {
  description = "EC2에 쓸 OS 이미지 ID"
}

variable "instance_type" {
  default = "t3.micro"
}

variable "desired_capacity" {
  default = 2
}

variable "min_size" {
  default = 1
}

variable "max_size" {
  default = 4
}

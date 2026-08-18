variable "aws_region" {
  description = "AWS 리전 (서울)"
  type        = string
  default     = "ap-northeast-2"
}

variable "vpc_cidr" {
  description = "VPC 전체 IP 대역"
  type        = string
  default     = "10.0.0.0/16"
}
variable "project_name" { type = string }
variable "nat_ami" {
  type        = string
  description = "NAT AMI. 빈 문자열이면 SSM latest Amazon Linux 2 사용"
  default     = ""
}
variable "public_subnet_id" { type = string }
variable "nat_sg_id" { type = string }
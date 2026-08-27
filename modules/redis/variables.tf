variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "private_app_subnet_ids" {
  type = list(string)
}

variable "redis_sg_id" {
  type = string
}

variable "node_type" {
  type    = string
  default = "cache.t3.micro"
}

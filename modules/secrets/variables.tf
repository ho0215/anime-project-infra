variable "project_name" {
  type    = string
  default = "aniverse"
}

variable "django_secret_key" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "gemini_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "db_name" {
  type    = string
  default = "aniverse"
}

variable "db_username" {
  type    = string
  default = "admin"
}

variable "db_host" {
  type = string
}

variable "db_port" {
  type    = number
  default = 3306
}

variable "static_bucket_name" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "domain_name" {
  type    = string
  default = ""
}

variable "use_https" {
  type    = bool
  default = true
}

variable "redis_url" {
  type    = string
  default = ""
}

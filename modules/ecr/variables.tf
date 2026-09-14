variable "project_name" {
  description = "리소스 태그용 프로젝트 이름"
  type        = string
}

variable "repository_name" {
  description = "ECR 리포지토리 이름 (예: aniverse)"
  type        = string
  default     = "aniverse"
}

variable "image_tag_mutability" {
  description = "MUTABLE 이면 latest 덮어쓰기 가능. 운영 sha 태그는 여전히 권장"
  type        = string
  default     = "MUTABLE"

  validation {
    condition     = contains(["MUTABLE", "IMMUTABLE"], var.image_tag_mutability)
    error_message = "image_tag_mutability must be MUTABLE or IMMUTABLE."
  }
}

variable "scan_on_push" {
  description = "푸시 시 이미지 취약점 스캔"
  type        = bool
  default     = true
}

variable "force_delete" {
  description = "리포 삭제 시 이미지가 있어도 강제 삭제 (랩/학습용)"
  type        = bool
  default     = true
}

variable "keep_image_count" {
  description = "라이프사이클으로 남길 최대 이미지 수"
  type        = number
  default     = 20
}

variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "project_name" {
  description = "리소스 이름 prefix"
  type        = string
  default     = "aniverse"
}

variable "vpc_cidr" {
  description = "VPC 전체 IP 대역"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "프라이빗 앱(EKS) 서브넷 IP 대역"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

# RDS는 더 이상 안 쓰지만, 서브넷 자체는 실제로 생성됨 — 지금은 Redis(ElastiCache,
# module.cache)가 이 서브넷을 씀. NAT SG ingress 허용 대역으로도 겸용.
variable "private_db_subnet_cidrs" {
  description = "프라이빗 DB 서브넷 CIDR (Redis/ElastiCache 배치, NAT SG ingress 허용용)"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24"]
}

variable "admin_cidr_blocks" {
  description = "EKS API 퍼블릭 접근 허용 CIDR"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "nat_ami" {
  description = "NAT 인스턴스 AMI. 비우면 SSM /ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"
  type        = string
  default     = ""
}

variable "static_bucket_name" {
  description = "정적/미디어 S3 버킷 base 이름 (뒤에 account-region 이 붙음)"
  type        = string
  # anime-project의 values-eks.yaml AWS_STORAGE_BUCKET_NAME, docs/scripts 전부
  # "aniverse-static-<account>-<region>" 형태를 가정하고 있음 — base는 "aniverse-static"으로 고정.
  default = "aniverse-static"
}

variable "domain_name" {
  description = "앱 도메인 (Route 53)"
  type        = string
  default     = "aniverse.my"
}

variable "subject_alternative_names" {
  description = "ACM SAN 목록"
  type        = list(string)
  default     = ["www.aniverse.my"]
}

variable "create_route53_zone" {
  description = "퍼블릭 호스팅 영역 관리(true 유지). destroy 시 존은 keep-dns 로 보존"
  type        = bool
  default     = true
}

variable "request_acm" {
  description = "ACM 인증서 + DNS 검증 레코드 생성 (ISSUED 대기는 안 함)"
  type        = bool
  default     = true
}

variable "eks_ingress_hostname" {
  description = "EKS Ingress ALB DNS 폴백 (lookup 실패 시). 보통 비움"
  type        = string
  default     = ""
}

variable "lookup_eks_alb" {
  description = "Ingress 태그로 ALB 자동 조회"
  type        = bool
  default     = true
}

variable "eks_ingress_stack" {
  description = "AWS LB Controller stack 태그 = namespace/ingress-name"
  type        = string
  default     = "aniverse/aniverse-web"
}

variable "ecr_repository_name" {
  description = "ECR 리포지토리 이름"
  type        = string
  default     = "aniverse"
}

variable "ecr_keep_image_count" {
  description = "ECR 라이프사이클으로 유지할 최대 이미지 수"
  type        = number
  default     = 20
}

variable "eks_cluster_version" {
  description = "비우면(null) AWS 기본 버전"
  type        = string
  default     = null
}

variable "eks_cluster_admin_arns" {
  description = "kubectl cluster-admin 추가 IAM ARN (로컬 SSO 사용자 등). CI Terraform 역할은 모듈이 자동 부여"
  type        = list(string)
  # AWSReservedSSO_AdministratorAccess 역할 — 서이(계정 소유/네트워크/보안/EKS), 현우(총괄/CI-CD)
  # 둘 다 이 권한 세트 공유. SSO 역할 하나당 access entry 하나라 두 사람이 같은 entry를 씀.
  default = ["arn:aws:iam::841535407395:role/aws-reserved/sso.amazonaws.com/ap-northeast-2/AWSReservedSSO_AdministratorAccess_e2fb8e5aead25e6d"]
}

variable "eks_edit_arns" {
  description = "aniverse_edit_namespaces로 범위 제한된 edit 등급 IAM ARN"
  type        = list(string)
  # AWSReservedSSO_aniverse-app-edit 역할 — 윤주(모니터링/DB), 유민(컴퓨트)
  default = ["arn:aws:iam::841535407395:role/aws-reserved/sso.amazonaws.com/ap-northeast-2/AWSReservedSSO_aniverse-app-edit_fbef725212ce072a"]
}

variable "eks_edit_namespaces" {
  description = "eks_edit_arns 접근 범위"
  type        = list(string)
  default     = ["aniverse", "monitoring"]
}

variable "eks_node_desired_size" {
  type    = number
  default = 2
}

variable "eks_node_min_size" {
  # min_size는 modules/eks에서 ignore_changes 처리됨 — 이 기본값은 신규 클러스터
  # 최초 생성 시에만 적용되고, 이후엔 eks-stop.sh/eks-start.sh나 지금처럼 AWS CLI로
  # 직접 바꾼 값이 유지됨(Terraform이 되돌리지 않음).
  type    = number
  default = 2
}

variable "eks_node_max_size" {
  type    = number
  default = 4
}

variable "eks_node_instance_types" {
  type    = list(string)
  default = ["t3.medium"]
}

variable "eks_node_capacity_type" {
  description = "ON_DEMAND | SPOT"
  type        = string
  default     = "ON_DEMAND"
}

variable "eks_enable_aws_lb_controller" {
  type    = bool
  default = true
}

variable "eks_enable_cluster_autoscaler" {
  type    = bool
  default = true
}

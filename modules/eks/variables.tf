variable "project_name" {
  description = "리소스 이름 prefix"
  type        = string
}

variable "vpc_id" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "public_subnet_ids" {
  description = "internet-facing ALB(Ingress)용 — kubernetes.io/role/elb 태그를 붙임"
  type        = list(string)
}

variable "private_app_subnet_ids" {
  description = "EKS 클러스터 ENI + 워커 노드가 위치할 서브넷"
  type        = list(string)
}

variable "cluster_version" {
  description = "EKS 버전. 비워두면(null) AWS가 기본(최신 지원) 버전을 사용"
  type        = string
  default     = null
}

variable "cluster_public_access_cidrs" {
  description = "EKS API 퍼블릭 엔드포인트 접근 허용 CIDR (kubectl/CI용)"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "cluster_admin_arns" {
  description = "aws-auth 대신 access entry로 cluster-admin 부여할 추가 IAM 사용자/역할 ARN (로컬 kubectl용). CI 역할은 클러스터 생성자 권한으로 자동 포함됨"
  type        = list(string)
  default     = []
}

# scripts/eks-start.sh · .github/workflows/eks-start-stop.yml 기본값과 반드시 일치
variable "node_desired_size" {
  type    = number
  default = 2
}

variable "node_min_size" {
  type    = number
  default = 0
}

variable "node_max_size" {
  type    = number
  default = 4
}

variable "node_instance_types" {
  type    = list(string)
  default = ["t3.medium"]
}

variable "node_capacity_type" {
  description = "ON_DEMAND | SPOT"
  type        = string
  default     = "ON_DEMAND"
}

variable "enable_aws_lb_controller" {
  description = "AWS Load Balancer Controller Helm 설치 여부 (Ingress → ALB)"
  type        = bool
  default     = true
}

variable "lb_controller_chart_version" {
  type    = string
  default = "1.11.0"
}

variable "lb_controller_iam_policy_ref" {
  description = "aws-load-balancer-controller 공식 IAM 정책을 받아오는 GitHub 태그 (버전 올릴 때만 변경)"
  type        = string
  default     = "v2.11.0"
}

variable "enable_cluster_autoscaler" {
  description = "Cluster Autoscaler Helm 설치 여부 (노드 오토스케일)"
  type        = bool
  default     = true
}

variable "cluster_autoscaler_chart_version" {
  type    = string
  default = "9.43.2"
}

variable "app_s3_bucket_arn" {
  description = "앱 web Pod IRSA용 S3 버킷 ARN — enable_app_s3_irsa일 때 정책 Resource로만 쓰임"
  type        = string
  default     = ""
}

# count를 이 값(정적 bool)으로 결정 — app_s3_bucket_arn(모듈 출력값이라 완전 빈 state에서
# apply 전엔 unknown)으로 count를 계산하면 "Invalid count argument" 에러가 남.
variable "enable_app_s3_irsa" {
  description = "web Pod IRSA(S3) 생성 여부. plan 시점에 알려진 bool 이어야 함 (버킷 ARN 으로 count 하지 말 것)"
  type        = bool
  default     = false
}

variable "app_irsa_namespace" {
  description = "앱 ServiceAccount 네임스페이스"
  type        = string
  default     = "aniverse"
}

variable "app_irsa_service_account" {
  description = "앱 web ServiceAccount 이름 (Helm values serviceAccount.name)"
  type        = string
  default     = "aniverse-web"
}

variable "db_backup_s3_bucket_arn" {
  description = "DB 백업(mysqldump) 저장용 S3 버킷 ARN — enable_db_backup_irsa일 때 정책 Resource로만 쓰임"
  type        = string
  default     = ""
}

# count를 이 값(정적 bool)으로 결정 — 이유는 enable_app_s3_irsa 주석 참고.
variable "enable_db_backup_irsa" {
  description = "DB 백업 CronJob IRSA(S3) 생성 여부. plan 시점에 알려진 bool 이어야 함"
  type        = bool
  default     = false
}

variable "db_backup_s3_prefix" {
  description = "버킷 안 백업 파일 경로 — IAM 권한을 이 prefix로만 제한 (static/media는 접근 불가)"
  type        = string
  default     = "db-backups"
}

variable "db_backup_irsa_namespace" {
  description = "백업 CronJob ServiceAccount 네임스페이스"
  type        = string
  default     = "aniverse"
}

variable "db_backup_irsa_service_account" {
  description = "백업 CronJob이 쓰는 ServiceAccount 이름 — CronJob yaml의 serviceAccountName과 일치해야 함"
  type        = string
  default     = "aniverse-db-backup"
}

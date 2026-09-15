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

# scripts/eks-ctl.sh, .github/workflows/eks-start-stop.yml 기본값과 반드시 일치
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

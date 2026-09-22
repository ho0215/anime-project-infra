data "aws_region" "current" {}

# ==========================================
# 클러스터(컨트롤 플레인) IAM
# ==========================================
resource "aws_iam_role" "cluster" {
  name = "${var.project_name}-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "eks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  role       = aws_iam_role.cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

# ==========================================
# 클러스터 (컨트롤 플레인)
# 클러스터 보안그룹은 지정하지 않음 → EKS가 자동 생성/관리(매니지드 노드그룹에
# 자동 연결되어 컨트롤 플레인 ↔ 노드 통신을 기본 허용, 별도 SG 배선 불필요)
# ==========================================
resource "aws_eks_cluster" "this" {
  name     = "${var.project_name}-eks"
  role_arn = aws_iam_role.cluster.arn
  version  = var.cluster_version

  vpc_config {
    subnet_ids              = var.private_app_subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.cluster_public_access_cidrs
  }

  access_config {
    authentication_mode                         = "API"
    bootstrap_cluster_creator_admin_permissions = true
  }

  depends_on = [aws_iam_role_policy_attachment.cluster_policy]

  tags = { Name = "${var.project_name}-eks" }
}

# 로컬 kubectl 등 CI 역할 외 추가 관리자 (클러스터 생성자는 access_config로 자동 admin)
resource "aws_eks_access_entry" "admins" {
  for_each      = toset(var.cluster_admin_arns)
  cluster_name  = aws_eks_cluster.this.name
  principal_arn = each.value
}

resource "aws_eks_access_policy_association" "admins" {
  for_each      = toset(var.cluster_admin_arns)
  cluster_name  = aws_eks_cluster.this.name
  principal_arn = each.value
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }

  depends_on = [aws_eks_access_entry.admins]
}

# ==========================================
# IRSA: OIDC 프로바이더 (파드 단위 IAM)
# ==========================================
data "tls_certificate" "eks" {
  url = aws_eks_cluster.this.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  url             = aws_eks_cluster.this.identity[0].oidc[0].issuer
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
}

locals {
  oidc_provider = replace(aws_iam_openid_connect_provider.eks.url, "https://", "")
}

# ==========================================
# 워커 노드 그룹 IAM (노드 단위 권한)
# ==========================================
resource "aws_iam_role" "node" {
  name = "${var.project_name}-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "node_worker" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "node_cni" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "node_ecr_ro" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# 기존 EC2(compute 모듈)와 동일하게 SSH 대신 SSM으로 노드 디버깅
resource "aws_iam_role_policy_attachment" "node_ssm" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# ==========================================
# 워커 노드 그룹 (매니지드) + 오토스케일링 범위
# node_group_name은 scripts/eks-start.sh · eks-start-stop.yml 기본값(aniverse-nodes)과 일치해야 함
# desired_size는 eks-start.sh/eks-stop.sh가 AWS API로 직접 바꾸므로,
# terraform apply(CD가 main push마다 돎)가 그 값을 되돌리지 않도록 ignore_changes 처리
# ==========================================
resource "aws_eks_node_group" "default" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "${var.project_name}-nodes"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_app_subnet_ids

  instance_types = var.node_instance_types
  capacity_type  = var.node_capacity_type
  ami_type       = "AL2023_x86_64_STANDARD"

  scaling_config {
    desired_size = var.node_desired_size
    min_size     = var.node_min_size
    max_size     = var.node_max_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = { role = "app" }

  # Cluster Autoscaler ASG 자동탐색용 (EKS가 노드그룹 태그를 하위 ASG에 전파)
  tags = {
    "k8s.io/cluster-autoscaler/enabled"                      = "true"
    "k8s.io/cluster-autoscaler/${aws_eks_cluster.this.name}" = "owned"
  }

  depends_on = [
    aws_iam_role_policy_attachment.node_worker,
    aws_iam_role_policy_attachment.node_cni,
    aws_iam_role_policy_attachment.node_ecr_ro,
  ]

  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }
}

# ==========================================
# 서브넷 태그 — ALB/NLB 자동탐색(AWS Load Balancer Controller)에 필요
# for_each + toset(subnet_ids) 는 서브넷이 같은 apply에서 만들어질 때
# ID가 plan 시점에 unknown → "Invalid for_each argument" 로 막힘.
# count + index 는 length만 알면 되므로 VPC와 같이 첫 apply 가능.
# ==========================================
resource "aws_ec2_tag" "public_elb" {
  count       = length(var.public_subnet_ids)
  resource_id = var.public_subnet_ids[count.index]
  key         = "kubernetes.io/role/elb"
  value       = "1"
}

resource "aws_ec2_tag" "public_cluster" {
  count       = length(var.public_subnet_ids)
  resource_id = var.public_subnet_ids[count.index]
  key         = "kubernetes.io/cluster/${aws_eks_cluster.this.name}"
  value       = "shared"
}

resource "aws_ec2_tag" "private_internal_elb" {
  count       = length(var.private_app_subnet_ids)
  resource_id = var.private_app_subnet_ids[count.index]
  key         = "kubernetes.io/role/internal-elb"
  value       = "1"
}

resource "aws_ec2_tag" "private_cluster" {
  count       = length(var.private_app_subnet_ids)
  resource_id = var.private_app_subnet_ids[count.index]
  key         = "kubernetes.io/cluster/${aws_eks_cluster.this.name}"
  value       = "shared"
}

# ==========================================
# EKS 애드온 — VPC CNI / kube-proxy / CoreDNS / EBS CSI
# ==========================================
resource "aws_eks_addon" "vpc_cni" {
  cluster_name                = aws_eks_cluster.this.name
  addon_name                  = "vpc-cni"
  resolve_conflicts_on_update = "OVERWRITE"

  # anime-project deploy/k8s/base/networkpolicy.yaml(aniverse-db-allow-web-only)가
  # EKS에서도 그대로 강제될 거라 가정하고 있음. VPC CNI는 기본값으로는 NetworkPolicy를
  # 무시(미강제)하므로 명시적으로 켜야 그 가정이 맞음.
  configuration_values = jsonencode({
    enableNetworkPolicy = "true"
  })
}

resource "aws_eks_addon" "kube_proxy" {
  cluster_name                = aws_eks_cluster.this.name
  addon_name                  = "kube-proxy"
  resolve_conflicts_on_update = "OVERWRITE"
}

resource "aws_eks_addon" "coredns" {
  cluster_name                = aws_eks_cluster.this.name
  addon_name                  = "coredns"
  resolve_conflicts_on_update = "OVERWRITE"

  # CoreDNS 파드가 뜰 노드가 있어야 함
  depends_on = [aws_eks_node_group.default]
}

# anime-project deploy/helm/aniverse의 HPA(hpa.yaml)가 CPU 사용률 기준으로 스케일함.
# metrics-server 없인 HPA가 "unknown" 상태로 멈춰서 min/maxReplicas가 있어도 동작 안 함.
resource "aws_eks_addon" "metrics_server" {
  cluster_name                = aws_eks_cluster.this.name
  addon_name                  = "metrics-server"
  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [aws_eks_node_group.default]
}

# ---- EBS CSI: IRSA ----
data "aws_iam_policy_document" "ebs_csi_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:sub"
      values   = ["system:serviceaccount:kube-system:ebs-csi-controller-sa"]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ebs_csi" {
  name               = "${var.project_name}-ebs-csi-irsa"
  assume_role_policy = data.aws_iam_policy_document.ebs_csi_assume.json
}

resource "aws_iam_role_policy_attachment" "ebs_csi" {
  role       = aws_iam_role.ebs_csi.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}

resource "aws_eks_addon" "ebs_csi" {
  cluster_name                = aws_eks_cluster.this.name
  addon_name                  = "aws-ebs-csi-driver"
  service_account_role_arn    = aws_iam_role.ebs_csi.arn
  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [aws_eks_node_group.default]
}

# gp3 StorageClass — anime-project values-eks.yaml의 storageClassName: "gp3" 대상
resource "kubernetes_storage_class" "gp3" {
  metadata {
    name = "gp3"
    annotations = {
      "storageclass.kubernetes.io/is-default-class" = "true"
    }
  }

  storage_provisioner    = "ebs.csi.aws.com"
  reclaim_policy         = "Delete"
  volume_binding_mode    = "WaitForFirstConsumer"
  allow_volume_expansion = true

  parameters = {
    type      = "gp3"
    encrypted = "true"
  }

  depends_on = [aws_eks_addon.ebs_csi]
}

# ==========================================
# AWS Load Balancer Controller — Ingress → ALB (파드 단위 IRSA)
# 공식 IAM 정책은 upstream(GitHub) 원본을 그대로 사용 — 직접 옮겨적지 않음
# ==========================================
data "http" "lb_controller_iam_policy" {
  count = var.enable_aws_lb_controller ? 1 : 0
  url   = "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/${var.lb_controller_iam_policy_ref}/docs/install/iam_policy.json"
}

resource "aws_iam_policy" "lb_controller" {
  count  = var.enable_aws_lb_controller ? 1 : 0
  name   = "${var.project_name}-aws-lb-controller"
  policy = data.http.lb_controller_iam_policy[0].response_body
}

data "aws_iam_policy_document" "lb_controller_assume" {
  count = var.enable_aws_lb_controller ? 1 : 0

  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:sub"
      values   = ["system:serviceaccount:kube-system:aws-load-balancer-controller"]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lb_controller" {
  count              = var.enable_aws_lb_controller ? 1 : 0
  name               = "${var.project_name}-lb-controller-irsa"
  assume_role_policy = data.aws_iam_policy_document.lb_controller_assume[0].json
}

resource "aws_iam_role_policy_attachment" "lb_controller" {
  count      = var.enable_aws_lb_controller ? 1 : 0
  role       = aws_iam_role.lb_controller[0].name
  policy_arn = aws_iam_policy.lb_controller[0].arn
}

resource "helm_release" "aws_load_balancer_controller" {
  count      = var.enable_aws_lb_controller ? 1 : 0
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  version    = var.lb_controller_chart_version

  set {
    name  = "clusterName"
    value = aws_eks_cluster.this.name
  }

  set {
    name  = "region"
    value = data.aws_region.current.name
  }

  set {
    name  = "vpcId"
    value = var.vpc_id
  }

  set {
    name  = "serviceAccount.create"
    value = "true"
  }

  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = aws_iam_role.lb_controller[0].arn
  }

  depends_on = [aws_eks_node_group.default, aws_eks_addon.vpc_cni, aws_eks_addon.coredns]
}

# ==========================================
# Cluster Autoscaler — 노드 단위 오토스케일링 (파드 단위 IRSA)
# ==========================================
data "aws_iam_policy_document" "cluster_autoscaler_assume" {
  count = var.enable_cluster_autoscaler ? 1 : 0

  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:sub"
      values   = ["system:serviceaccount:kube-system:cluster-autoscaler"]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "cluster_autoscaler" {
  count              = var.enable_cluster_autoscaler ? 1 : 0
  name               = "${var.project_name}-cluster-autoscaler-irsa"
  assume_role_policy = data.aws_iam_policy_document.cluster_autoscaler_assume[0].json
}

resource "aws_iam_role_policy" "cluster_autoscaler" {
  count = var.enable_cluster_autoscaler ? 1 : 0
  name  = "${var.project_name}-cluster-autoscaler"
  role  = aws_iam_role.cluster_autoscaler[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ClusterAutoscalerRead"
        Effect = "Allow"
        Action = [
          "autoscaling:DescribeAutoScalingGroups",
          "autoscaling:DescribeAutoScalingInstances",
          "autoscaling:DescribeLaunchConfigurations",
          "autoscaling:DescribeScalingActivities",
          "autoscaling:DescribeTags",
          "ec2:DescribeInstanceTypes",
          "ec2:DescribeLaunchTemplateVersions",
          "eks:DescribeNodegroup",
        ]
        Resource = "*"
      },
      {
        Sid    = "ClusterAutoscalerWrite"
        Effect = "Allow"
        Action = [
          "autoscaling:SetDesiredCapacity",
          "autoscaling:TerminateInstanceInAutoScalingGroup",
          "autoscaling:UpdateAutoScalingGroup",
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "autoscaling:ResourceTag/k8s.io/cluster-autoscaler/${aws_eks_cluster.this.name}" = "owned"
          }
        }
      },
    ]
  })
}

resource "helm_release" "cluster_autoscaler" {
  count      = var.enable_cluster_autoscaler ? 1 : 0
  name       = "cluster-autoscaler"
  repository = "https://kubernetes.github.io/autoscaler"
  chart      = "cluster-autoscaler"
  namespace  = "kube-system"
  version    = var.cluster_autoscaler_chart_version

  set {
    name  = "autoDiscovery.clusterName"
    value = aws_eks_cluster.this.name
  }

  set {
    name  = "awsRegion"
    value = data.aws_region.current.name
  }

  set {
    name  = "rbac.serviceAccount.name"
    value = "cluster-autoscaler"
  }

  set {
    name  = "rbac.serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = aws_iam_role.cluster_autoscaler[0].arn
  }

  # 컨트롤 플레인 버전과 나란히 — 값 없으면 chart 기본 이미지 태그 사용
  set {
    name  = "extraArgs.balance-similar-node-groups"
    value = "true"
  }

  depends_on = [aws_eks_node_group.default, aws_eks_addon.vpc_cni]
}

# ==========================================
# App web Pod IRSA — S3 media/static put (aniverse-web SA)
# ==========================================
data "aws_iam_policy_document" "app_s3_assume" {
  count = var.enable_app_s3_irsa ? 1 : 0

  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:sub"
      values   = ["system:serviceaccount:${var.app_irsa_namespace}:${var.app_irsa_service_account}"]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "app_s3" {
  count              = var.enable_app_s3_irsa ? 1 : 0
  name               = "${var.project_name}-web-s3-irsa"
  assume_role_policy = data.aws_iam_policy_document.app_s3_assume[0].json
}

resource "aws_iam_role_policy" "app_s3" {
  count = var.enable_app_s3_irsa ? 1 : 0
  name  = "${var.project_name}-web-s3"
  role  = aws_iam_role.app_s3[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListBucket"
        Effect   = "Allow"
        Action   = ["s3:ListBucket", "s3:GetBucketLocation"]
        Resource = [var.app_s3_bucket_arn]
      },
      {
        Sid    = "ObjectRW"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:AbortMultipartUpload",
          "s3:ListMultipartUploadParts",
        ]
        Resource = ["${var.app_s3_bucket_arn}/*"]
      },
    ]
  })
}

# ==========================================
# DB 백업 CronJob Pod IRSA — mysqldump를 S3에 put (윤주 CronJob yaml)
# 같은 static 버킷을 쓰되 db_backup_s3_prefix 경로로만 권한 범위를 좁힘
# (static/media 파일엔 손 못 대게 — 최소 권한).
# ==========================================
data "aws_iam_policy_document" "db_backup_assume" {
  count = var.enable_db_backup_irsa ? 1 : 0

  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:sub"
      values   = ["system:serviceaccount:${var.db_backup_irsa_namespace}:${var.db_backup_irsa_service_account}"]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "db_backup" {
  count              = var.enable_db_backup_irsa ? 1 : 0
  name               = "${var.project_name}-db-backup-irsa"
  assume_role_policy = data.aws_iam_policy_document.db_backup_assume[0].json
}

resource "aws_iam_role_policy" "db_backup" {
  count = var.enable_db_backup_irsa ? 1 : 0
  name  = "${var.project_name}-db-backup-s3"
  role  = aws_iam_role.db_backup[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListBackupPrefixOnly"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = [var.db_backup_s3_bucket_arn]
        Condition = {
          StringLike = { "s3:prefix" = ["${var.db_backup_s3_prefix}/*"] }
        }
      },
      {
        Sid    = "BackupObjectRW"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
        ]
        Resource = ["${var.db_backup_s3_bucket_arn}/${var.db_backup_s3_prefix}/*"]
      },
    ]
  })
}

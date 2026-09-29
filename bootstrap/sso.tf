# EKS 차등 권한(edit 등급)용 SSO Permission Set + Group.
# 콘솔에서 먼저 만들고(2026-09-29) 나중에 코드로 편입(terraform import) — 실제 값과
# 어긋나면 plan에서 diff로 드러남, 그때 코드를 실제 상태에 맞춰 조정.
#
# cluster-admin 쪽(AdministratorAccess 권한 세트, aniverse-admin 그룹)은 더 이전에
# 콘솔로 만들어졌고 아직 코드 편입 안 함 — 필요해지면 같은 패턴으로 추가.

data "aws_ssoadmin_instances" "this" {}

locals {
  sso_instance_arn  = tolist(data.aws_ssoadmin_instances.this.arns)[0]
  identity_store_id = tolist(data.aws_ssoadmin_instances.this.identity_store_ids)[0]
}

# ── Permission Set: aniverse-app-edit ──────────────────────
# EKS 쪽 실제 권한(무엇을 할 수 있는지)은 modules/eks의 AmazonEKSEditPolicy access
# entry가 전부 담당 — 여기 IAM 정책은 "클러스터를 describe/list할 수 있다" 정도의
# 최소 권한만 있으면 됨(aws eks update-kubeconfig / exec-credential 발급에 필요).
resource "aws_ssoadmin_permission_set" "app_edit" {
  name             = "aniverse-app-edit"
  instance_arn     = local.sso_instance_arn
  session_duration = "PT12H"
}

resource "aws_ssoadmin_permission_set_inline_policy" "app_edit" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.app_edit.arn

  inline_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["eks:DescribeCluster", "eks:ListClusters"]
        Resource = "*"
      },
    ]
  })
}

# ── Group: aniverse-edit (윤주, 유민) ───────────────────────
resource "aws_identitystore_group" "aniverse_edit" {
  identity_store_id = local.identity_store_id
  display_name      = "aniverse-edit"
}

# 사용자 ID는 identitystore에서 조회한 고정값 — 콘솔에서 생성된 실제 사용자.
locals {
  aniverse_edit_members = {
    "younju-developer" = "a418ddfc-7051-7053-6fd9-c2740df6beb4"
    "yumin-developer"  = "b4a8ed7c-d011-7008-cef8-46cf5e357b96"
  }
}

resource "aws_identitystore_group_membership" "aniverse_edit" {
  for_each = local.aniverse_edit_members

  identity_store_id = local.identity_store_id
  group_id          = aws_identitystore_group.aniverse_edit.group_id
  member_id         = each.value
}

# ── 계정 할당: aniverse-edit 그룹 → aniverse-app-edit 권한 세트 (이 AWS 계정) ──
# aws_caller_identity.current는 github_oidc.tf에 이미 선언되어 있어 재사용.
resource "aws_ssoadmin_account_assignment" "aniverse_edit" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.app_edit.arn

  principal_id   = aws_identitystore_group.aniverse_edit.group_id
  principal_type = "GROUP"

  target_id   = data.aws_caller_identity.current.account_id
  target_type = "AWS_ACCOUNT"
}

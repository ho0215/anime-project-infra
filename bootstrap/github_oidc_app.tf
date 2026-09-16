# GitHub Actions (anime-project) → ECR push 전용 OIDC 역할
# infra Terraform Admin 역할과 분리 — 앱 CI는 ECR만 가정
#
# bootstrap apply 후 anime-project Variables:
#   AWS_ROLE_ARN  = github_actions_app_ecr_role_arn
#   AWS_USE_OIDC  = true

variable "github_app_repo" {
  description = "OIDC 신뢰 대상 앱 저장소"
  type        = string
  default     = "anime-project"
}

variable "ecr_repository_name" {
  description = "앱 이미지 ECR 리포지토리 이름"
  type        = string
  default     = "aniverse"
}

data "aws_iam_policy_document" "github_app_ecr_assume" {
  statement {
    sid    = "GitHubActionsAppEcrOIDC"
    effect = "Allow"
    actions = [
      "sts:AssumeRoleWithWebIdentity",
      "sts:TagSession",
    ]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:${var.github_org}/${var.github_app_repo}:*",
        "repo:${var.github_org}@*/${var.github_app_repo}@*:*",
      ]
    }
  }
}

resource "aws_iam_role" "github_actions_app_ecr" {
  name               = "aniverse-github-actions-ecr"
  assume_role_policy = data.aws_iam_policy_document.github_app_ecr_assume.json

  tags = {
    Name = "aniverse-github-actions-ecr"
  }
}

variable "static_bucket_name_for_ci" {
  description = "앱 CI가 media/static sync 할 S3 버킷 (비우면 S3 권한 미부여)"
  type        = string
  default     = "aniverse-static-679583587966-ap-northeast-2"
}

data "aws_iam_policy_document" "github_app_ecr" {
  statement {
    sid    = "EcrAuthToken"
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "EcrPushAniverse"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:BatchGetImage",
      "ecr:DescribeImages",
      "ecr:DescribeRepositories",
      "ecr:ListImages",
      "ecr:GetDownloadUrlForLayer",
    ]
    resources = [
      "arn:aws:ecr:ap-northeast-2:${data.aws_caller_identity.current.account_id}:repository/${var.ecr_repository_name}",
    ]
  }

  # DB 복구 후 media sync / collectstatic 용 (bootstrap apply 후 유효)
  dynamic "statement" {
    for_each = var.static_bucket_name_for_ci != "" ? [var.static_bucket_name_for_ci] : []
    content {
      sid    = "StaticMediaBucketSync"
      effect = "Allow"
      actions = [
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:GetBucketPolicy",
        "s3:PutBucketPolicy",
        "s3:PutBucketPublicAccessBlock",
        "s3:PutBucketOwnershipControls",
        "s3:PutBucketCors",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
      ]
      resources = [
        "arn:aws:s3:::${statement.value}",
        "arn:aws:s3:::${statement.value}/*",
      ]
    }
  }
}

resource "aws_iam_role_policy" "github_actions_app_ecr" {
  name   = "aniverse-github-actions-ecr-push"
  role   = aws_iam_role.github_actions_app_ecr.id
  policy = data.aws_iam_policy_document.github_app_ecr.json
}

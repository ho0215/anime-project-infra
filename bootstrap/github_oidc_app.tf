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
}

resource "aws_iam_role_policy" "github_actions_app_ecr" {
  name   = "aniverse-github-actions-ecr-push"
  role   = aws_iam_role.github_actions_app_ecr.id
  policy = data.aws_iam_policy_document.github_app_ecr.json
}

# GitHub Actions → AWS OIDC (장기 Access Key 대체)
# bootstrap apply 후:
#   - infra 레포 Variable AWS_ROLE_ARN = github_actions_role_arn
#   - infra 레포 Variable AWS_USE_OIDC = true
#
# AWS IAM 규칙: trust 에 반드시 범위가 있는
#   token.actions.githubusercontent.com:sub  (또는 job_workflow_ref)
# StringEquals/StringLike 조건이 있어야 한다. repository 클레임만으로는 거부됨.
#
# GitHub environment 를 job 에 붙이면 sub 가
#   repo:ORG/REPO:environment:NAME
# 으로 바뀌어 trust 와 어긋나기 쉽다 → CD 는 environment 미사용.
#
# sub 예시:
#   repo:ho0215/anime-project-infra:ref:refs/heads/main
#   repo:ho0215@123/anime-project-infra@456:ref:refs/heads/main

data "aws_caller_identity" "current" {}

variable "github_org" {
  type    = string
  default = "ho0215"
}

variable "github_repo" {
  description = "OIDC 신뢰 대상 infra 저장소"
  type        = string
  default     = "anime-project-infra"
}

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
  ]

  tags = {
    Name = "github-actions-oidc"
  }
}

data "aws_iam_policy_document" "github_assume" {
  statement {
    sid    = "GitHubActionsOIDC"
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

    # 저장소로 범위 제한 (AWS가 요구하는 sub 조건). 전체 "*" 단독은 거부됨.
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:${var.github_org}/${var.github_repo}:*",
        "repo:${var.github_org}@*/${var.github_repo}@*:*",
      ]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "aniverse-github-actions-terraform"
  assume_role_policy = data.aws_iam_policy_document.github_assume.json

  tags = {
    Name = "aniverse-github-actions-terraform"
  }
}

# 학습/포트폴리오: Terraform 전체 리소스 관리. 운영에서는 최소 권한으로 축소.
resource "aws_iam_role_policy_attachment" "github_actions_admin" {
  role       = aws_iam_role.github_actions.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

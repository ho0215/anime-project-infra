# GitHub Actions → AWS OIDC (장기 Access Key 대체)
# bootstrap apply 후 GitHub Actions Variable AWS_ROLE_ARN 에 role ARN 등록
#
# CD job 은 environment: production 을 쓰므로 sub 가
#   repo:ORG/REPO:environment:production
# 형태가 된다. 2026-07 이후 생성/옵트인 저장소는 immutable ID 가 붙을 수 있어
# sub 와일드카드보다 repository 클레임으로 신뢰하는 편이 안전하다.

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
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  # GitHub 루트 CA 교체 대비 — AWS는 목록 중 일치하는 지문만 사용
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
    # configure-aws-credentials@v4+ 는 TagSession 도 요청할 수 있음
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

    # immutable sub(repo:user@id/repo@id:...) 에도 동일한 값
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:repository"
      values   = ["${var.github_org}/${var.github_repo}"]
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

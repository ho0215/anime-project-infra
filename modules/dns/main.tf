# aniverse.my Route53 + ACM DNS 검증 레코드 + EKS ALB alias
#
# 호스팅 영역(NS)은 비용·가비아 위임 때문에 destroy 해도 지우지 않는다.
# (lifecycle.prevent_destroy + scripts/terraform-destroy-keep-dns.sh)
# EKS ALB 는 Ingress 태그로 조회 — 재생성 후 apply 하면 alias 가 자동 갱신.

data "aws_lb_hosted_zone_id" "alb" {
  region             = var.aws_region
  load_balancer_type = "application"
}

resource "aws_route53_zone" "main" {
  count = var.create_zone ? 1 : 0
  name  = var.domain_name

  tags = {
    Name    = "${var.project_name}-public"
    Project = var.project_name
  }

  lifecycle {
    prevent_destroy = true
  }
}

data "aws_route53_zone" "existing" {
  count        = var.create_zone ? 0 : 1
  name         = var.domain_name
  private_zone = false
}

locals {
  zone_id      = var.create_zone ? aws_route53_zone.main[0].zone_id : data.aws_route53_zone.existing[0].zone_id
  name_servers = var.create_zone ? aws_route53_zone.main[0].name_servers : data.aws_route53_zone.existing[0].name_servers
}

# Ingress(AWS LB Controller)가 붙인 태그로 ALB 자동 탐색
data "aws_lbs" "eks_ingress" {
  count = var.lookup_eks_alb ? 1 : 0

  tags = {
    "ingress.k8s.aws/stack" = var.eks_ingress_stack
  }
}

locals {
  # aws_lbs.arns 는 set — list 로 변환 후 첫 ALB 사용
  eks_alb_arn = var.lookup_eks_alb ? try(tolist(data.aws_lbs.eks_ingress[0].arns)[0], "") : ""
}

data "aws_lb" "eks_ingress" {
  count = local.eks_alb_arn != "" ? 1 : 0
  arn   = local.eks_alb_arn
}

locals {
  # 1) 태그로 찾은 ALB  2) 변수 폴백(최초/수동)  3) 아직 둘 다 없으면(첫 apply 등) ""
  # coalesce()는 인자 전부가 null/빈 문자열이면 그 자체로 에러를 내서 ""를 폴백으로
  # 못 씀 — 바깥을 try()로 한 번 더 감싸서 그 에러를 ""로 흡수함.
  eks_alb_dns = try(
    coalesce(
      try(data.aws_lb.eks_ingress[0].dns_name, null),
      var.eks_alb_dns_name != "" ? var.eks_alb_dns_name : null,
    ),
    ""
  )
}

# apex / www → EKS Ingress ALB (ALB 있을 때만)
resource "aws_route53_record" "eks_apex" {
  count   = local.eks_alb_dns != "" ? 1 : 0
  zone_id = local.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = local.eks_alb_dns
    zone_id                = data.aws_lb_hosted_zone_id.alb.id
    evaluate_target_health = true
  }

  allow_overwrite = true
}

resource "aws_route53_record" "eks_www" {
  count   = local.eks_alb_dns != "" && contains(var.subject_alternative_names, "www.${var.domain_name}") ? 1 : 0
  zone_id = local.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name                   = local.eks_alb_dns
    zone_id                = data.aws_lb_hosted_zone_id.alb.id
    evaluate_target_health = true
  }

  allow_overwrite = true
}

# ACM — DNS 검증 레코드만. ISSUED 대기는 안 함.
# 인증서도 가능하면 유지하는 편이 HTTPS 재기동이 빠름(destroy 스크립트에서 제외).
resource "aws_acm_certificate" "main" {
  count                     = var.request_acm ? 1 : 0
  domain_name               = var.domain_name
  subject_alternative_names = var.subject_alternative_names
  validation_method         = "DNS"

  tags = {
    Name = "${var.project_name}-cert"
  }

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = true
  }
}

resource "aws_route53_record" "cert_validation" {
  for_each = var.request_acm ? {
    for dvo in aws_acm_certificate.main[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = local.zone_id
}

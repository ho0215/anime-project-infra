# aniverse.my Route53 + (옵션) ACM DNS 검증 레코드 + EKS ALB alias
#
# 존이 지워진 뒤 복구용. 새 존 NS 를 가비아에 위임해야 외부 해석/ACM 발급이 완료됨.

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
}

data "aws_route53_zone" "existing" {
  count        = var.create_zone ? 0 : 1
  name         = var.domain_name
  private_zone = false
}

locals {
  zone_id      = var.create_zone ? aws_route53_zone.main[0].zone_id : data.aws_route53_zone.existing[0].zone_id
  zone_name    = var.create_zone ? aws_route53_zone.main[0].name : data.aws_route53_zone.existing[0].name
  name_servers = var.create_zone ? aws_route53_zone.main[0].name_servers : data.aws_route53_zone.existing[0].name_servers
}

# apex / www → EKS Ingress ALB
resource "aws_route53_record" "eks_apex" {
  count   = var.eks_alb_dns_name != "" ? 1 : 0
  zone_id = local.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = var.eks_alb_dns_name
    zone_id                = data.aws_lb_hosted_zone_id.alb.id
    evaluate_target_health = true
  }

  allow_overwrite = true
}

resource "aws_route53_record" "eks_www" {
  count   = var.eks_alb_dns_name != "" && contains(var.subject_alternative_names, "www.${var.domain_name}") ? 1 : 0
  zone_id = local.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name                   = var.eks_alb_dns_name
    zone_id                = data.aws_lb_hosted_zone_id.alb.id
    evaluate_target_health = true
  }

  allow_overwrite = true
}

# ACM — DNS 검증 레코드만 만들고, ISSUED 대기는 하지 않음 (NS 위임 전엔 영원히 Pending)
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

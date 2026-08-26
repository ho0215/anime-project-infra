resource "aws_secretsmanager_secret" "app" {
  name                    = "${var.project_name}/app-runtime"
  description             = "Aniverse Django/RDS/Gemini runtime secrets"
  recovery_window_in_days = 0

  tags = {
    Name = "${var.project_name}-app-runtime"
  }
}

locals {
  allowed_hosts = var.domain_name != "" ? "${var.domain_name},www.${var.domain_name}" : "*"
  csrf_trusted_origins = var.domain_name != "" ? (
    var.use_https
    ? "https://${var.domain_name},https://www.${var.domain_name}"
    : "http://${var.domain_name},http://www.${var.domain_name}"
  ) : "http://*.elb.amazonaws.com,https://*.elb.amazonaws.com"

  secret_payload = {
    DJANGO_SECRET_KEY           = var.django_secret_key
    DJANGO_DEBUG                = "False"
    DJANGO_ALLOWED_HOSTS        = local.allowed_hosts
    DJANGO_CSRF_TRUSTED_ORIGINS = local.csrf_trusted_origins
    USE_HTTPS                   = var.use_https ? "True" : "False"
    DB_NAME                     = var.db_name
    DB_USER                     = var.db_username
    DB_PASSWORD                 = var.db_password
    DB_HOST                     = var.db_host
    DB_PORT                     = tostring(var.db_port)
    AWS_STORAGE_BUCKET_NAME     = var.static_bucket_name
    AWS_S3_REGION_NAME          = var.aws_region
    AWS_ACCESS_KEY_ID           = ""
    AWS_SECRET_ACCESS_KEY       = ""
    GEMINI_API_KEY              = var.gemini_api_key
    GEMINI_MODEL                = "gemini-3.6-flash"
    REDIS_URL                   = var.redis_url
  }
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id     = aws_secretsmanager_secret.app.id
  secret_string = jsonencode(local.secret_payload)
}

#!/usr/bin/env bash
# Idempotent bootstrap on each EC2 launch (ASG Launch Template user_data).
# Terraform templatefile() injects placeholders such as efs_dns_name / db_host below.
set -euxo pipefail

sleep 5
export DEBIAN_FRONTEND=noninteractive

# Retry apt — NAT/VPC may not be ready on first boot
for i in 1 2 3 4 5; do
  apt-get update -y && break
  sleep 5
done

# OS packages needed for:
# - mysqlclient pip build (libmysqlclient-dev / pkg-config / python3-dev / build-essential)
# - nginx (ALB health before CodeDeploy)
# - CodeDeploy agent (ruby)
# - EFS / AWS CLI
# - SSM Session Manager agent (.deb)
apt-get install -y \
  ruby-full wget curl unzip \
  awscli nfs-common \
  python3 python3-venv python3-pip python3-dev \
  build-essential pkg-config default-libmysqlclient-dev \
  nginx

PROJECT_DIR="/home/ubuntu/aniverse"
MEDIA_DIR="$PROJECT_DIR/media"
ENV_FILE="$PROJECT_DIR/.env"
EFS_DNS="${efs_dns_name}"
AWS_REGION="${aws_region}"

mkdir -p "$PROJECT_DIR" "$MEDIA_DIR" "$PROJECT_DIR/staticfiles"
chown -R ubuntu:ubuntu "$PROJECT_DIR"

# ── SSM Agent (Ubuntu 22.04 does not ship it by default) ─
# Prefer snap; fall back to official .deb from S3.
if ! systemctl is-active --quiet snap.amazon-ssm-agent.amazon-ssm-agent.service \
  && ! systemctl is-active --quiet amazon-ssm-agent; then
  if snap install amazon-ssm-agent --classic; then
    systemctl enable --now snap.amazon-ssm-agent.amazon-ssm-agent.service || true
  else
    cd /tmp
    wget -q "https://s3.${aws_region}.amazonaws.com/amazon-ssm-${aws_region}/latest/debian_amd64/amazon-ssm-agent.deb" \
      -O amazon-ssm-agent.deb
    dpkg -i amazon-ssm-agent.deb || apt-get install -f -y
    systemctl enable --now amazon-ssm-agent
  fi
fi

# ── Temporary nginx /health/ so ALB does not kill the instance
#    before the first CodeDeploy finishes installing Django. ──
cat > /etc/nginx/sites-available/aniverse <<'NGINX'
server {
    listen 80 default_server;
    server_name _;
    client_max_body_size 128M;

    location /health/ {
        default_type text/plain;
        return 200 'ok';
    }

    location /static/ {
        alias /home/ubuntu/aniverse/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/aniverse/media/;
    }

    location / {
        return 503;
    }
}
NGINX
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/aniverse /etc/nginx/sites-enabled/aniverse
nginx -t
systemctl enable nginx
systemctl restart nginx

# ── EFS 마운트 (ASG 인스턴스 간 media 공유) ──────────────
if ! mountpoint -q "$MEDIA_DIR"; then
  if mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 \
    "$EFS_DNS:/" "$MEDIA_DIR"; then
    grep -q "$EFS_DNS" /etc/fstab || \
      echo "$EFS_DNS:/ $MEDIA_DIR nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,_netdev 0 0" >> /etc/fstab
  else
    echo "WARN: EFS mount failed for $EFS_DNS" | tee /var/log/aniverse-efs-mount.warn
  fi
fi
chown -R ubuntu:ubuntu "$MEDIA_DIR" || true

# ── Django 런타임 환경파일 ───────────────────────────────
# 값은 반드시 따옴표로 감싼다. (SECRET_KEY 에 ) 등이 있으면
# bash source / 일부 파서가 깨진다. Django-environ · systemd 모두 인용 지원.)
cat > "$ENV_FILE" <<EOF
DJANGO_SECRET_KEY='${django_secret_key}'
DJANGO_DEBUG=False
DB_NAME='${db_name}'
DB_USER='${db_username}'
DB_PASSWORD='${db_password}'
DB_HOST='${db_host}'
DB_PORT='${db_port}'
AWS_STORAGE_BUCKET_NAME='${static_bucket_name}'
AWS_S3_REGION_NAME='${aws_region}'
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
USE_HTTPS=${use_https}
DJANGO_ALLOWED_HOSTS='${allowed_hosts}'
GEMINI_API_KEY='${gemini_api_key}'
GEMINI_MODEL='gemini-3.6-flash'
DJANGO_CSRF_TRUSTED_ORIGINS='${csrf_trusted_origins}'
EOF
chown ubuntu:ubuntu "$ENV_FILE"
chmod 600 "$ENV_FILE"
cp "$ENV_FILE" /etc/aniverse.env
chmod 600 /etc/aniverse.env

# ── Daphne systemd unit (NOT enabled yet — venv appears after CodeDeploy)
cat > /etc/systemd/system/aniverse.service <<'UNIT'
[Unit]
Description=Aniverse Django (Daphne ASGI)
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/aniverse
EnvironmentFile=-/home/ubuntu/aniverse/.env
EnvironmentFile=-/etc/aniverse.env
ExecStart=/home/ubuntu/aniverse/venv/bin/daphne \
  -b 127.0.0.1 \
  -p 8000 \
  --access-log /home/ubuntu/aniverse/daphne-access.log \
  --proxy-headers \
  config.asgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
# Do not enable/start here: venv/daphne do not exist until CodeDeploy.

# ── CodeDeploy Agent ─────────────────────────────────────
cd /tmp
wget -q "https://aws-codedeploy-${aws_region}.s3.${aws_region}.amazonaws.com/latest/install"
chmod +x ./install
./install auto
systemctl enable codedeploy-agent
systemctl start codedeploy-agent

echo "user_data bootstrap complete (ssm + nginx health + build deps + codedeploy)"

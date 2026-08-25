#!/usr/bin/env bash
# Idempotent bootstrap on each EC2 launch (ASG Launch Template user_data).
# Values in TF_TEMPLATE_* form are injected by Terraform templatefile().
set -euxo pipefail

sleep 5
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ruby-full wget curl awscli nfs-common python3 python3-venv python3-pip

PROJECT_DIR="/home/ubuntu/aniverse"
MEDIA_DIR="$PROJECT_DIR/media"
ENV_FILE="$PROJECT_DIR/.env"
EFS_DNS="${efs_dns_name}"
AWS_REGION="${aws_region}"

mkdir -p "$PROJECT_DIR" "$MEDIA_DIR"
chown -R ubuntu:ubuntu "$PROJECT_DIR"

# ── EFS 마운트 (ASG 인스턴스 간 media 공유) ──────────────
if ! mountpoint -q "$MEDIA_DIR"; then
  mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 \
    "$EFS_DNS:/" "$MEDIA_DIR" || true
  if mountpoint -q "$MEDIA_DIR"; then
    grep -q "$EFS_DNS" /etc/fstab || \
      echo "$EFS_DNS:/ $MEDIA_DIR nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,_netdev 0 0" >> /etc/fstab
  fi
fi
chown -R ubuntu:ubuntu "$MEDIA_DIR" || true

# ── Django 런타임 환경파일 ───────────────────────────────
# CodeDeploy 가 앱 디렉터리를 동기화해도 보존되도록 /etc 에도 복사한다.
cat > "$ENV_FILE" <<EOF
DJANGO_SECRET_KEY=${django_secret_key}
DJANGO_DEBUG=False
DB_NAME=${db_name}
DB_USER=${db_username}
DB_PASSWORD=${db_password}
DB_HOST=${db_host}
DB_PORT=${db_port}
AWS_STORAGE_BUCKET_NAME=${static_bucket_name}
AWS_S3_REGION_NAME=${aws_region}
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
EOF
chown ubuntu:ubuntu "$ENV_FILE"
chmod 600 "$ENV_FILE"
cp "$ENV_FILE" /etc/aniverse.env
chmod 600 /etc/aniverse.env

# ── Gunicorn systemd 유닛 ───────────────────────────────
cat > /etc/systemd/system/aniverse.service <<'UNIT'
[Unit]
Description=Aniverse Django (Gunicorn)
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/aniverse
EnvironmentFile=-/home/ubuntu/aniverse/.env
EnvironmentFile=-/etc/aniverse.env
ExecStart=/home/ubuntu/aniverse/venv/bin/gunicorn \
  --bind 127.0.0.1:8000 \
  --workers 2 \
  --worker-class sync \
  --access-logfile /home/ubuntu/aniverse/gunicorn-access.log \
  --error-logfile /home/ubuntu/aniverse/gunicorn-error.log \
  config.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable aniverse.service

# ── CodeDeploy Agent ─────────────────────────────────────
cd /tmp
wget -q "https://aws-codedeploy-${aws_region}.s3.${aws_region}.amazonaws.com/latest/install"
chmod +x ./install
./install auto
systemctl enable codedeploy-agent
systemctl start codedeploy-agent

echo "user_data bootstrap complete"

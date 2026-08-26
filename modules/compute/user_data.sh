#!/usr/bin/env bash
# Idempotent bootstrap on each EC2 launch (ASG Launch Template user_data).
# Secrets come from AWS Secrets Manager (app_secret_arn) — not embedded in LT.
set -euxo pipefail

sleep 5
export DEBIAN_FRONTEND=noninteractive

for i in 1 2 3 4 5; do
  apt-get update -y && break
  sleep 5
done

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
export AWS_REGION="${aws_region}"
export APP_SECRET_ARN="${app_secret_arn}"
export ENV_FILE

mkdir -p "$PROJECT_DIR" "$MEDIA_DIR" "$PROJECT_DIR/staticfiles"
chown -R ubuntu:ubuntu "$PROJECT_DIR"

# ── SSM Agent ───────────────────────────────────────────
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

# ── Temporary nginx /health/ ─────────────────────────────
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

# ── EFS 마운트 ───────────────────────────────────────────
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

# ── Secrets Manager → .env (plaintext not in Launch Template) ─
python3 <<'PY'
import json, os, subprocess, time, sys

arn = os.environ["APP_SECRET_ARN"]
region = os.environ["AWS_REGION"]
path = os.environ["ENV_FILE"]
raw = None
for _ in range(8):
    try:
        raw = subprocess.check_output(
            [
                "aws", "secretsmanager", "get-secret-value",
                "--secret-id", arn, "--region", region,
                "--query", "SecretString", "--output", "text",
            ],
            text=True,
        )
        break
    except subprocess.CalledProcessError:
        time.sleep(5)
if not raw:
    sys.exit(f"failed to fetch secret {arn}")

data = json.loads(raw)
order = [
    "DJANGO_SECRET_KEY", "DJANGO_DEBUG", "DJANGO_ALLOWED_HOSTS",
    "DJANGO_CSRF_TRUSTED_ORIGINS", "USE_HTTPS",
    "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT",
    "AWS_STORAGE_BUCKET_NAME", "AWS_S3_REGION_NAME",
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
    "GEMINI_API_KEY", "GEMINI_MODEL", "REDIS_URL",
]
lines = []
for key in order:
    if key not in data:
        continue
    val = "" if data[key] is None else str(data[key])
    safe = val.replace("'", "'\"'\"'")
    lines.append(f"{key}='{safe}'")
open(path, "w").write("\n".join(lines) + "\n")
PY
chown ubuntu:ubuntu "$ENV_FILE"
chmod 600 "$ENV_FILE"
cp "$ENV_FILE" /etc/aniverse.env
chmod 600 /etc/aniverse.env

# ── Daphne systemd unit ──────────────────────────────────
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

# ── CodeDeploy Agent ─────────────────────────────────────
cd /tmp
wget -q "https://aws-codedeploy-${aws_region}.s3.${aws_region}.amazonaws.com/latest/install"
chmod +x ./install
./install auto
systemctl enable codedeploy-agent
systemctl start codedeploy-agent

echo "user_data bootstrap complete (ssm + secrets + nginx health + codedeploy)"

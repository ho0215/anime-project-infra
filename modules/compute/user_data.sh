#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log) 2>&1

# 1. 필요한 프로그램 설치
yum update -y
yum install -y nginx python3 python3-pip amazon-efs-utils

# 2. 김윤주님의 EFS(공유저장소) 연결
mkdir -p /mnt/efs
mount -t efs ${efs_id}:/ /mnt/efs
echo "${efs_id}:/ /mnt/efs efs defaults,_netdev 0 0" >> /etc/fstab

# 3. Gunicorn 설치 및 실행 등록 (Django 실행 담당)
pip3 install gunicorn django

cat > /etc/systemd/system/gunicorn.service << 'EOF'
[Unit]
Description=Gunicorn daemon
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/app
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 myproject.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gunicorn
systemctl start gunicorn

# 4. Nginx 설정 (요청을 받아서 Gunicorn한테 전달)
cat > /etc/nginx/conf.d/app.conf << 'EOF'
server {
    listen 80;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

systemctl enable nginx
systemctl restart nginx

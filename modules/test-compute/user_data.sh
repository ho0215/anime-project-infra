#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log) 2>&1

# 1. 필요한 패키지 설치
yum update -y
yum install -y nginx python3 python3-pip

# 2. Gunicorn 설치
pip3 install gunicorn

# 3. 테스트용 간단한 앱 만들기 (실제 Django 앱 대신 지금은 "작동 확인용")
mkdir -p /home/ec2-user/app
cat > /home/ec2-user/app/app.py << 'EOF'
def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b"Hello from Gunicorn! EC2 test success."]
EOF

# 4. Gunicorn을 systemd 서비스로 등록
cat > /etc/systemd/system/gunicorn.service << 'EOF'
[Unit]
Description=Gunicorn daemon
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/app
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gunicorn
systemctl start gunicorn

# 5. Nginx가 Gunicorn한테 요청 전달하도록 설정
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

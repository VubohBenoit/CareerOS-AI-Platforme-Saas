#!/bin/bash
set -e

echo "🚀 Starting CareerOS AI Backend Setup..."

# Update system
apt-get update
apt-get upgrade -y
apt-get install -y python3 python3-pip python3-venv git curl

# Clone repository
cd /home/ubuntu
git clone ${github_repo} careerosai
cd careerosai/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://${db_username}:${db_password}@${db_endpoint}/careerosdb
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
JWT_EXPIRATION_HOURS=24
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
EOF

# Update permissions
chown -R ubuntu:ubuntu /home/ubuntu/careerosai

# Create systemd service
sudo tee /etc/systemd/system/careerosai.service > /dev/null << 'SERVICE'
[Unit]
Description=CareerOS AI Backend
After=network.target postgresql.service

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/careerosai/backend
Environment="PATH=/home/ubuntu/careerosai/backend/venv/bin"
EnvironmentFile=/home/ubuntu/careerosai/backend/.env
ExecStart=/home/ubuntu/careerosai/backend/venv/bin/gunicorn \
  app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable careerosai
sudo systemctl start careerosai

# Wait for service to be ready
sleep 5
curl http://localhost:8000/health || true

echo "✅ CareerOS AI Backend Setup Complete!"
echo "Backend running on http://0.0.0.0:8000"
echo "API docs available at http://0.0.0.0:8000/api/docs"

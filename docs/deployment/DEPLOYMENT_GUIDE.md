# NVC Banking Platform - Deployment Guide

## Overview

This guide covers deployment strategies for the NVC Banking Platform across different environments, from development to production.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Servers   │    │    Database     │
│    (Nginx)      │────│   (Gunicorn)    │────│  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │     Cache       │              │
         └──────────────│    (Redis)      │──────────────┘
                        └─────────────────┘
```

## 🚀 Quick Deployment

### Development Environment

```bash
# Clone repository
git clone https://github.com/nvcfund/nvcfund-2.0.0.git
cd nvcfund-2.0.0

# Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r nvcfund-backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python nvcfund-backend/scripts/setup_postgres.py

# Run development server
python main.py
```

### Production Environment (Ubuntu 22.04)

```bash
# System dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql-14 redis-server nginx

# Create application user
sudo useradd -m -s /bin/bash nvcfund
sudo usermod -aG sudo nvcfund

# Switch to application user
sudo su - nvcfund

# Clone and setup application
git clone https://github.com/nvcfund/nvcfund-2.0.0.git
cd nvcfund-2.0.0
python3.11 -m venv venv
source venv/bin/activate
pip install -r nvcfund-backend/requirements.txt

# Configure production environment
cp .env.production .env
# Edit .env with production settings

# Setup database
sudo -u postgres createdb nvc_banking_prod
python nvcfund-backend/scripts/setup_postgres.py --production

# Run with Gunicorn
gunicorn --config gunicorn.conf.py main:app
```

## 🔧 Environment Configuration

### Environment Variables

Create `.env` file with the following variables:

```bash
# Application Settings
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DEBUG=false

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/nvc_banking_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis
CACHE_DEFAULT_TIMEOUT=300

# Security Settings
WTF_CSRF_ENABLED=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# AWS Configuration (Production)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=nvc-banking-assets

# Secrets Management
VAULT_URL=https://vault.nvcfund.com
VAULT_TOKEN=your-vault-token
AWS_SECRETS_MANAGER_REGION=us-east-1

# Email Configuration
MAIL_SERVER=smtp.nvcfund.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=noreply@nvcfund.com
MAIL_PASSWORD=your-email-password

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
METRICS_ENABLED=true

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
RATELIMIT_DEFAULT=1000 per hour
```

### Configuration Files

#### Gunicorn Configuration (`gunicorn.conf.py`)

```python
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/nvcfund/access.log"
errorlog = "/var/log/nvcfund/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "nvc-banking-platform"

# Server mechanics
daemon = False
pidfile = "/var/run/nvcfund/gunicorn.pid"
user = "nvcfund"
group = "nvcfund"
tmp_upload_dir = None

# SSL (if using HTTPS directly with Gunicorn)
# keyfile = "/path/to/ssl/private.key"
# certfile = "/path/to/ssl/certificate.crt"

# Worker tuning
preload_app = True
worker_tmp_dir = "/dev/shm"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

#### Nginx Configuration

```nginx
# /etc/nginx/sites-available/nvc-banking
upstream nvc_banking {
    server 127.0.0.1:8000;
    # Add more servers for load balancing
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name nvcfund.com www.nvcfund.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name nvcfund.com www.nvcfund.com;
    
    # SSL Configuration
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self'; frame-ancestors 'none';";
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Client body size
    client_max_body_size 10M;
    
    # Static files
    location /static/ {
        alias /home/nvcfund/nvcfund-2.0.0/nvcfund-backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /home/nvcfund/nvcfund-2.0.0/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Application
    location / {
        proxy_pass http://nvc_banking;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://nvc_banking;
    }
    
    # Block access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ \.(env|ini|conf)$ {
        deny all;
    }
}
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main.py

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY nvcfund-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "main:app"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/nvc_banking
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=nvc_banking
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## ☁️ AWS Deployment

### EC2 Deployment Script

```bash
#!/bin/bash
# deploy_aws.sh

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql-client redis-tools nginx awscli

# Create application directory
sudo mkdir -p /opt/nvcfund
sudo chown ubuntu:ubuntu /opt/nvcfund

# Clone application
cd /opt/nvcfund
git clone https://github.com/nvcfund/nvcfund-2.0.0.git
cd nvcfund-2.0.0

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r nvcfund-backend/requirements.txt

# Configure environment
aws secretsmanager get-secret-value --secret-id nvc-banking-prod --query SecretString --output text > .env

# Setup systemd service
sudo tee /etc/systemd/system/nvc-banking.service > /dev/null <<EOF
[Unit]
Description=NVC Banking Platform
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/nvcfund/nvcfund-2.0.0
Environment=PATH=/opt/nvcfund/nvcfund-2.0.0/venv/bin
ExecStart=/opt/nvcfund/nvcfund-2.0.0/venv/bin/gunicorn --config gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable nvc-banking
sudo systemctl start nvc-banking

# Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/nvc-banking
sudo ln -s /etc/nginx/sites-available/nvc-banking /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

echo "Deployment completed successfully!"
```

### RDS Configuration

```python
# Database configuration for RDS
import os

class ProductionConfig:
    # RDS Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@nvc-banking-prod.cluster-xyz.us-east-1.rds.amazonaws.com:5432/nvc_banking'
    
    # Connection pooling for RDS
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30
    }
    
    # SSL for RDS
    SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {
        'sslmode': 'require'
    }
```

## 📊 Monitoring & Logging

### Application Monitoring

```python
# monitoring.py
import logging
from flask import request, g
import time
import psutil

def setup_monitoring(app):
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        duration = time.time() - g.start_time
        
        # Log request metrics
        app.logger.info(
            f"Request: {request.method} {request.path} "
            f"Status: {response.status_code} "
            f"Duration: {duration:.3f}s "
            f"Memory: {psutil.virtual_memory().percent}%"
        )
        
        return response
```

### Log Configuration

```python
# logging_config.py
import logging
import logging.handlers
import os

def setup_logging(app):
    if not app.debug:
        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/nvc-banking.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Syslog handler for production
        if os.environ.get('SENTRY_DSN'):
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            
            sentry_sdk.init(
                dsn=os.environ.get('SENTRY_DSN'),
                integrations=[FlaskIntegration()],
                traces_sample_rate=0.1
            )
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('NVC Banking Platform startup')
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r nvcfund-backend/requirements.txt
      - name: Run tests
        run: |
          python run_tests.py --all
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to EC2
        env:
          PRIVATE_KEY: ${{ secrets.EC2_SSH_KEY }}
          HOSTNAME: ${{ secrets.EC2_HOSTNAME }}
          USER_NAME: ubuntu
        run: |
          echo "$PRIVATE_KEY" > private_key && chmod 600 private_key
          ssh -o StrictHostKeyChecking=no -i private_key ${USER_NAME}@${HOSTNAME} '
            cd /opt/nvcfund/nvcfund-2.0.0 &&
            git pull origin main &&
            source venv/bin/activate &&
            pip install -r nvcfund-backend/requirements.txt &&
            sudo systemctl restart nvc-banking
          '
```

## 🔐 Security Considerations

### SSL/TLS Configuration

```bash
# Generate SSL certificate with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d nvcfund.com -d www.nvcfund.com
```

### Firewall Configuration

```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Database Security

```sql
-- Create dedicated database user
CREATE USER nvc_banking_app WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE nvc_banking TO nvc_banking_app;
GRANT USAGE ON SCHEMA public TO nvc_banking_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nvc_banking_app;
```

## 📈 Performance Optimization

### Database Optimization

```python
# Connection pooling
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 30
}

# Query optimization
from sqlalchemy import text

# Use raw SQL for complex queries
result = db.session.execute(text("""
    SELECT account_id, SUM(amount) as total
    FROM transactions 
    WHERE created_at >= :start_date
    GROUP BY account_id
"""), {'start_date': start_date})
```

### Caching Strategy

```python
# Redis caching
from flask_caching import Cache

cache = Cache()

@cache.memoize(timeout=300)
def get_account_balance(account_id):
    # Expensive calculation
    return balance

# Cache invalidation
@cache.delete_memoized('get_account_balance')
def update_account_balance(account_id, new_balance):
    # Update balance and invalidate cache
    pass
```

This deployment guide provides comprehensive instructions for deploying the NVC Banking Platform across different environments with proper security, monitoring, and performance considerations.

# AWS Deployment Guide - NVC Banking Platform

## Table of Contents
1. [Overview](#overview)
2. [AWS Architecture](#aws-architecture)
3. [Prerequisites](#prerequisites)
4. [DNS Configuration (nvcfund.com)](#dns-configuration-nvcfundcom)
5. [Infrastructure Setup](#infrastructure-setup)
6. [Database Setup (RDS PostgreSQL)](#database-setup-rds-postgresql)
7. [Backend Deployment (EC2 + Nginx)](#backend-deployment-ec2--nginx)
8. [EC2 Instance Upgrade (T2 to T3 Micro)](#ec2-instance-upgrade-t2-to-t3-micro)
9. [Frontend Deployment (S3 + CloudFront)](#frontend-deployment-s3--cloudfront)
10. [Security & Secrets Management](#security--secrets-management)
11. [Load Balancing & Auto Scaling](#load-balancing--auto-scaling)
12. [AWS Console GUI Guide](#aws-console-gui-guide)
13. [Monitoring & Logging](#monitoring--logging)
14. [Troubleshooting](#troubleshooting)

## Overview

This guide provides comprehensive instructions for deploying the NVC Banking Platform on AWS using production-ready infrastructure. The deployment architecture ensures high availability, security, and scalability suitable for enterprise banking operations.

> **Note**: For standard Python server deployment (VPS, dedicated servers), see [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)

### Deployment Architecture
- **Domain**: nvcfund.com (Hostgator DNS provider with Route 53 delegation)
- **Backend**: Flask application on Ubuntu EC2 with Nginx reverse proxy
- **Database**: AWS RDS PostgreSQL with Multi-AZ deployment
- **Frontend**: React SPA hosted on S3 with CloudFront CDN
- **Security**: AWS Secrets Manager with Boto3 integration (already implemented)
- **Monitoring**: CloudWatch for logging and metrics
- **Load Balancing**: Application Load Balancer with Auto Scaling
- **Instance Type**: Seamless upgrade from T2.micro to T3.micro for better performance

## AWS Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          AWS Cloud                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐│
│  │   CloudFront    │    │ Application     │    │   Route 53      ││
│  │   (CDN)         │    │ Load Balancer   │    │   (DNS)         ││
│  └─────────────────┘    └─────────────────┘    └─────────────────┘│
│           │                       │                       │        │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐│
│  │   S3 Bucket     │    │   EC2 Instances │    │   AWS Secrets   ││
│  │   (Frontend)    │    │   (Backend)     │    │   Manager       ││
│  └─────────────────┘    └─────────────────┘    └─────────────────┘│
│                                   │                                │
│                          ┌─────────────────┐                      │
│                          │   RDS PostgreSQL│                      │
│                          │   (Multi-AZ)    │                      │
│                          └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### AWS Account Requirements
- AWS Account with appropriate permissions
- AWS CLI configured with access keys
- Domain name registered (optional but recommended)

### Local Development Environment
- Python 3.11+
- Node.js 18+
- Git
- Docker (optional for containerization)

### AWS CLI Installation
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

## DNS Configuration (nvcfund.com)

### 1. Hostgator DNS to Route 53 Delegation
Since your domain is managed by Hostgator, you'll need to delegate DNS to AWS Route 53 for seamless integration with AWS services.

#### Step 1: Create Route 53 Hosted Zone
```bash
# Create hosted zone for nvcfund.com
aws route53 create-hosted-zone \
    --name nvcfund.com \
    --caller-reference nvcfund-$(date +%s) \
    --hosted-zone-config Comment="NVC Fund Banking Platform hosted zone"

# Get the nameservers
aws route53 list-resource-record-sets \
    --hosted-zone-id Z1D633PJN98FT9 \
    --query "ResourceRecordSets[?Type=='NS'].ResourceRecords[].Value" \
    --output table
```

#### Step 2: Update Hostgator DNS Settings
1. **Login to Hostgator Control Panel**
2. **Navigate to DNS Management**
3. **Update Name Servers** to AWS Route 53 nameservers:
   ```
   ns-1234.awsdns-56.org
   ns-789.awsdns-01.net
   ns-456.awsdns-23.com
   ns-012.awsdns-78.co.uk
   ```

#### Step 3: Configure DNS Records
```bash
# Create A record for main domain
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1D633PJN98FT9 \
    --change-batch '{
        "Changes": [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "nvcfund.com",
                    "Type": "A",
                    "AliasTarget": {
                        "DNSName": "your-alb-dns-name.us-east-2.elb.amazonaws.com",
                        "EvaluateTargetHealth": true,
                        "HostedZoneId": "Z35SXDOTRQ7X7K"
                    }
                }
            }
        ]
    }'

# Create CNAME for www subdomain
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1D633PJN98FT9 \
    --change-batch '{
        "Changes": [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "www.nvcfund.com",
                    "Type": "CNAME",
                    "TTL": 300,
                    "ResourceRecords": [
                        {
                            "Value": "nvcfund.com"
                        }
                    ]
                }
            }
        ]
    }'

# Create API subdomain for backend services
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1D633PJN98FT9 \
    --change-batch '{
        "Changes": [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "api.nvcfund.com",
                    "Type": "A",
                    "AliasTarget": {
                        "DNSName": "your-alb-dns-name.us-east-2.elb.amazonaws.com",
                        "EvaluateTargetHealth": true,
                        "HostedZoneId": "Z35SXDOTRQ7X7K"
                    }
                }
            }
        ]
    }'
```

### 4. SSL Certificate for nvcfund.com
```bash
# Request SSL certificate using ACM
aws acm request-certificate \
    --domain-name nvcfund.com \
    --subject-alternative-names www.nvcfund.com api.nvcfund.com \
    --validation-method DNS \
    --region us-east-2

# Get certificate validation records
aws acm describe-certificate \
    --certificate-arn arn:aws:acm:us-east-2:123456789012:certificate/12345678-1234-1234-1234-123456789012 \
    --query 'Certificate.DomainValidationOptions'
```

## Infrastructure Setup

### 1. VPC and Networking
```bash
# Create VPC
aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=nvc-banking-vpc}]'

# Create Internet Gateway
aws ec2 create-internet-gateway \
    --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=nvc-banking-igw}]'

# Create Public Subnets (Multi-AZ)
aws ec2 create-subnet \
    --vpc-id vpc-xxxxxxxx \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-2a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=nvc-banking-public-1a}]'

aws ec2 create-subnet \
    --vpc-id vpc-xxxxxxxx \
    --cidr-block 10.0.2.0/24 \
    --availability-zone us-east-2b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=nvc-banking-public-2b}]'

# Create Private Subnets for RDS
aws ec2 create-subnet \
    --vpc-id vpc-xxxxxxxx \
    --cidr-block 10.0.3.0/24 \
    --availability-zone us-east-2a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=nvc-banking-private-2a}]'

aws ec2 create-subnet \
    --vpc-id vpc-xxxxxxxx \
    --cidr-block 10.0.4.0/24 \
    --availability-zone us-east-2b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=nvc-banking-private-2b}]'
```

### 2. Security Groups
```bash
# Create security group for web servers
aws ec2 create-security-group \
    --group-name nvc-banking-web-sg \
    --description "Security group for NVC Banking web servers" \
    --vpc-id vpc-xxxxxxxx

# Allow HTTP, HTTPS, and SSH
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Create security group for RDS
aws ec2 create-security-group \
    --group-name nvc-banking-rds-sg \
    --description "Security group for NVC Banking RDS" \
    --vpc-id vpc-xxxxxxxx

# Allow PostgreSQL access from web servers
aws ec2 authorize-security-group-ingress \
    --group-id sg-rds-xxxxxxxx \
    --protocol tcp \
    --port 5432 \
    --source-group sg-web-xxxxxxxx
```

## Database Setup (RDS PostgreSQL)

### 1. Create DB Subnet Group
```bash
aws rds create-db-subnet-group \
    --db-subnet-group-name nvcfund-db-subnet-group \
    --db-subnet-group-description "Subnet group for NVC Banking database" \
    --subnet-ids subnet-xxxxxxxx subnet-yyyyyyyy
```

### 2. Create RDS PostgreSQL Instance
```bash
aws rds create-db-instance \
    --db-instance-identifier nvcfund-db \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --engine-version 15.4 \
    --master-username nvcdba \
    --master-user-password $(aws secretsmanager get-random-password --password-length 32 --exclude-characters '"@/\' --query 'RandomPassword' --output text) \
    --allocated-storage 100 \
    --storage-type gp3 \
    --storage-encrypted \
    --vpc-security-group-ids sg-rds-xxxxxxxx \
    --db-subnet-group-name nvcfund-db-subnet-group \
    --backup-retention-period 30 \
    --multi-az \
    --deletion-protection \
    --enable-performance-insights \
    --performance-insights-retention-period 7 \
    --db-name nvcfund_db
```

### 3. Database Schema Migration
```bash
# Create migration script
cat > migrate_db.py << 'EOF'
import os
import psycopg2
from sqlalchemy import create_engine
from app_factory import create_app
from modules.core.extensions import db

def migrate_database():
    """Apply database schema to RDS PostgreSQL"""
    app = create_app('production')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Run any custom migrations
        from modules.core.database_migration import apply_migrations
        apply_migrations()
        
        print("Database migration completed successfully")

if __name__ == "__main__":
    migrate_database()
EOF

# Run migration (after setting up EC2 instance)
python migrate_db.py
```

## Backend Deployment (EC2 + Nginx)

### 1. Launch EC2 Instance
```bash
# Create key pair
aws ec2 create-key-pair \
    --key-name nvc-banking-keypair \
    --key-type rsa \
    --query 'KeyMaterial' \
    --output text > nvc-banking-keypair.pem

chmod 400 nvc-banking-keypair.pem

# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.medium \
    --key-name nvc-banking-keypair \
    --security-group-ids sg-web-xxxxxxxx \
    --subnet-id subnet-xxxxxxxx \
    --user-data file://user-data.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=nvc-banking-web-server}]'
```

### 2. User Data Script for EC2
```bash
# Create user-data.sh
cat > user-data.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y python3.11 python3.11-pip git nginx redis

# Install Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
yum install -y nodejs

# Configure Python
alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1

# Create application user
useradd -m -s /bin/bash nvcapp
usermod -aG nginx nvcapp

# Clone repository
cd /home/nvcapp
git clone https://github.com/your-org/nvc-banking-platform.git
chown -R nvcapp:nvcapp nvc-banking-platform

# Install Python dependencies
cd nvc-banking-platform/nvcfund-backend
pip3 install -r requirements.txt
pip3 install gunicorn

# Start and enable services
systemctl start nginx
systemctl enable nginx
systemctl start redis
systemctl enable redis

# Install AWS CLI
pip3 install awscli
EOF
```

### 3. Application Deployment Script
```bash
# Create deployment script
cat > deploy_backend.sh << 'EOF'
#!/bin/bash
set -e

# Variables
APP_DIR="/home/nvcapp/nvc-banking-platform"
BACKEND_DIR="$APP_DIR/nvcfund-backend"
SERVICE_NAME="nvc-banking"

# Update application
cd $APP_DIR
git pull origin main

# Install/update dependencies
cd $BACKEND_DIR
pip3 install -r requirements.txt

# Get secrets from AWS Secrets Manager
export DATABASE_URL=$(aws secretsmanager get-secret-value --secret-id nvc-banking/database --query SecretString --output text | jq -r .DATABASE_URL)
export SESSION_SECRET=$(aws secretsmanager get-secret-value --secret-id nvc-banking/session --query SecretString --output text | jq -r .SESSION_SECRET)

# Run database migrations
python3 migrate_db.py

# Create systemd service
cat > /etc/systemd/system/$SERVICE_NAME.service << 'SERVICE'
[Unit]
Description=NVC Banking Platform
After=network.target

[Service]
Type=notify
User=nvcapp
Group=nvcapp
WorkingDirectory=/home/nvcapp/nvc-banking-platform/nvcfund-backend
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=FLASK_ENV=production
EnvironmentFile=/home/nvcapp/nvc-banking-platform/.env
ExecStart=/usr/local/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --worker-class sync --worker-connections 1000 --timeout 30 --keep-alive 5 --max-requests 1000 --max-requests-jitter 50 main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Start service
systemctl daemon-reload
systemctl start $SERVICE_NAME
systemctl enable $SERVICE_NAME

echo "Backend deployment completed successfully"
EOF

chmod +x deploy_backend.sh
```

## EC2 Instance Upgrade (T2 to T3 Micro)

### Seamless Instance Type Migration
Since you're currently running on T2.micro and want to upgrade to T3.micro for better performance, here's the seamless migration process:

#### 1. Current Setup Assessment
```bash
# Check current instance details
aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" \
    --query 'Reservations[].Instances[].[InstanceId,InstanceType,State.Name,Tags[?Key==`Name`].Value|[0]]' \
    --output table

# Verify Boto3 secrets management is working
python3 -c "
import boto3
try:
    client = boto3.client('secretsmanager')
    print('✓ Boto3 secrets management is configured correctly')
except Exception as e:
    print(f'✗ Boto3 error: {e}')
"
```

#### 2. Pre-Migration Backup
```bash
# Create AMI from current instance
aws ec2 create-image \
    --instance-id i-1234567890abcdef0 \
    --name "nvc-banking-t2-backup-$(date +%Y%m%d)" \
    --description "Backup before T3 migration" \
    --no-reboot

# Create snapshot of EBS volumes
aws ec2 describe-instances \
    --instance-ids i-1234567890abcdef0 \
    --query 'Reservations[].Instances[].BlockDeviceMappings[].Ebs.VolumeId' \
    --output text | xargs -I {} aws ec2 create-snapshot \
    --volume-id {} \
    --description "Pre-T3-migration backup"
```

#### 3. Zero-Downtime Migration Options

**Option A: Stop and Modify (Brief Downtime)**
```bash
# Stop the instance
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Wait for instance to stop
aws ec2 wait instance-stopped --instance-ids i-1234567890abcdef0

# Modify instance type
aws ec2 modify-instance-attribute \
    --instance-id i-1234567890abcdef0 \
    --instance-type Value=t3.micro

# Start the instance
aws ec2 start-instances --instance-ids i-1234567890abcdef0

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids i-1234567890abcdef0
```

**Option B: Blue-Green Deployment (Zero Downtime)**
```bash
# Launch new T3.micro instance with same configuration
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.micro \
    --key-name nvc-banking-keypair \
    --security-group-ids sg-web-xxxxxxxx \
    --subnet-id subnet-xxxxxxxx \
    --user-data file://user-data.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=nvc-banking-web-server-t3}]'

# Deploy application to new instance
./deploy_backend.sh

# Update load balancer targets
aws elbv2 register-targets \
    --target-group-arn arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/nvc-banking-targets/1234567890abcdef \
    --targets Id=i-new-instance-id

# Deregister old instance after health checks pass
aws elbv2 deregister-targets \
    --target-group-arn arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/nvc-banking-targets/1234567890abcdef \
    --targets Id=i-old-instance-id
```

#### 4. Post-Migration Verification
```bash
# Verify instance type change
aws ec2 describe-instances \
    --instance-ids i-1234567890abcdef0 \
    --query 'Reservations[].Instances[].[InstanceId,InstanceType,State.Name]' \
    --output table

# Test application functionality
curl -H "Host: nvcfund.com" http://your-instance-ip/health
curl -H "Host: api.nvcfund.com" http://your-instance-ip/api/v1/health

# Verify secrets management still works
ssh -i nvc-banking-keypair.pem ubuntu@your-instance-ip
python3 -c "
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='nvc-banking/database')
print('✓ Secrets management working on T3.micro')
"
```

### 4. Nginx Configuration
```nginx
# Create /etc/nginx/sites-available/nvc-banking
server {
    listen 80;
    server_name your-domain.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=banking:10m rate=10r/s;
    limit_req zone=banking burst=20 nodelay;
    
    # Proxy settings
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Static files
    location /static/ {
        alias /home/nvcapp/nvc-banking-platform/nvcfund-backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API and application routes
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_timeout 300s;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}

# SSL configuration (after obtaining SSL certificate)
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL optimization
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Include the same configuration as HTTP server
    include /etc/nginx/sites-available/nvc-banking-common;
}
```

### 5. SSL Certificate Setup
```bash
# Install Certbot
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Frontend Deployment (S3 + CloudFront)

### 1. Create S3 Bucket
```bash
# Create S3 bucket
aws s3 mb s3://nvc-banking-frontend-prod

# Configure bucket for static website hosting
aws s3 website s3://nvc-banking-frontend-prod \
    --index-document index.html \
    --error-document error.html

# Set bucket policy
cat > bucket-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::nvc-banking-frontend-prod/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket nvc-banking-frontend-prod \
    --policy file://bucket-policy.json
```

### 2. Build and Deploy Frontend
```bash
# Create frontend deployment script
cat > deploy_frontend.sh << 'EOF'
#!/bin/bash
set -e

# Variables
FRONTEND_DIR="nvcfund-frontend"
S3_BUCKET="nvc-banking-frontend-prod"
CLOUDFRONT_DISTRIBUTION_ID="E1234567890ABC"

# Build frontend
cd $FRONTEND_DIR
npm install
npm run build

# Deploy to S3
aws s3 sync build/ s3://$S3_BUCKET/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
    --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
    --paths "/*"

echo "Frontend deployment completed successfully"
EOF

chmod +x deploy_frontend.sh
```

### 3. CloudFront Configuration
```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
    --distribution-config file://cloudfront-config.json
```

```json
{
    "CallerReference": "nvc-banking-frontend-2025",
    "Comment": "NVC Banking Platform Frontend Distribution",
    "DefaultCacheBehavior": {
        "TargetOriginId": "nvc-banking-s3-origin",
        "ViewerProtocolPolicy": "redirect-to-https",
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000,
        "Compress": true
    },
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "nvc-banking-s3-origin",
                "DomainName": "nvc-banking-frontend-prod.s3.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                }
            }
        ]
    },
    "Enabled": true,
    "PriceClass": "PriceClass_All",
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            }
        ]
    }
}
```

## Security & Secrets Management

### 1. AWS Secrets Manager Setup
```bash
# Create database credentials secret
aws secretsmanager create-secret \
    --name nvc-banking/database \
    --description "Database credentials for NVC Banking Platform" \
    --secret-string '{
        "DATABASE_URL": "postgresql://nvcdba:password@nvcfund-db.cluster-xxxxx.us-east-2.rds.amazonaws.com:5432/nvcfund_db",
        "PGHOST": "nvcfund-db.cluster-xxxxx.us-east-2.rds.amazonaws.com",
        "PGPORT": "5432",
        "PGUSER": "nvcdba",
        "PGPASSWORD": "your-secure-password",
        "PGDATABASE": "nvcfund_db"
    }'

# Create session secret
aws secretsmanager create-secret \
    --name nvc-banking/session \
    --description "Session secret for NVC Banking Platform" \
    --secret-string '{
        "SESSION_SECRET": "'$(openssl rand -base64 32)'"
    }'

# Create application secrets
aws secretsmanager create-secret \
    --name nvc-banking/application \
    --description "Application secrets for NVC Banking Platform" \
    --secret-string '{
        "MAIL_USERNAME": "your-email@gmail.com",
        "MAIL_PASSWORD": "your-app-password",
        "PLAID_CLIENT_ID": "your-plaid-client-id",
        "PLAID_SECRET": "your-plaid-secret",
        "BINANCE_CLIENT_ID": "your-binance-client-id",
        "BINANCE_CLIENT_SECRET": "your-binance-secret"
    }'
```

### 2. IAM Roles and Policies
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": [
                "arn:aws:secretsmanager:us-east-2:123456789012:secret:nvc-banking/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "rds:DescribeDBInstances",
                "rds:DescribeDBClusters"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
```

### 3. Environment Configuration Script
```bash
# Create environment setup script
cat > setup_environment.sh << 'EOF'
#!/bin/bash
set -e

# Function to get secret from AWS Secrets Manager
get_secret() {
    local secret_name=$1
    local key=$2
    aws secretsmanager get-secret-value \
        --secret-id $secret_name \
        --query SecretString \
        --output text | jq -r .$key
}

# Create .env file
cat > .env << 'ENVFILE'
# Database Configuration
DATABASE_URL=$(get_secret "nvc-banking/database" "DATABASE_URL")
PGHOST=$(get_secret "nvc-banking/database" "PGHOST")
PGPORT=$(get_secret "nvc-banking/database" "PGPORT")
PGUSER=$(get_secret "nvc-banking/database" "PGUSER")
PGPASSWORD=$(get_secret "nvc-banking/database" "PGPASSWORD")
PGDATABASE=$(get_secret "nvc-banking/database" "PGDATABASE")

# Session Configuration
SESSION_SECRET=$(get_secret "nvc-banking/session" "SESSION_SECRET")

# Application Configuration
FLASK_ENV=production
MAIL_USERNAME=$(get_secret "nvc-banking/application" "MAIL_USERNAME")
MAIL_PASSWORD=$(get_secret "nvc-banking/application" "MAIL_PASSWORD")
PLAID_CLIENT_ID=$(get_secret "nvc-banking/application" "PLAID_CLIENT_ID")
PLAID_SECRET=$(get_secret "nvc-banking/application" "PLAID_SECRET")
BINANCE_CLIENT_ID=$(get_secret "nvc-banking/application" "BINANCE_CLIENT_ID")
BINANCE_CLIENT_SECRET=$(get_secret "nvc-banking/application" "BINANCE_CLIENT_SECRET")
ENVFILE

echo "Environment configuration completed"
EOF

chmod +x setup_environment.sh
```

## Monitoring & Logging

### 1. CloudWatch Configuration
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i amazon-cloudwatch-agent.deb

# Create CloudWatch agent configuration
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOF'
{
    "agent": {
        "metrics_collection_interval": 60,
        "run_as_user": "cwagent"
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/nvc-banking/application.log",
                        "log_group_name": "/aws/ec2/nvc-banking/application",
                        "log_stream_name": "{instance_id}"
                    },
                    {
                        "file_path": "/var/log/nginx/access.log",
                        "log_group_name": "/aws/ec2/nvc-banking/nginx-access",
                        "log_stream_name": "{instance_id}"
                    },
                    {
                        "file_path": "/var/log/nginx/error.log",
                        "log_group_name": "/aws/ec2/nvc-banking/nginx-error",
                        "log_stream_name": "{instance_id}"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "NVC/Banking",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_iowait", "cpu_usage_user", "cpu_usage_system"],
                "metrics_collection_interval": 60,
                "totalcpu": false
            },
            "disk": {
                "measurement": ["used_percent"],
                "metrics_collection_interval": 60,
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": 60
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

### 2. Application Logging Configuration
```python
# Add to config.py
import logging
from logging.handlers import RotatingFileHandler
import os

class ProductionConfig(Config):
    # ... existing configuration ...
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Configure logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            '/var/log/nvc-banking/application.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('NVC Banking Platform startup')
```

## Load Balancing & Auto Scaling

### Comprehensive Load Balancing and Auto Scaling Strategy
This section provides detailed configuration for high-availability load balancing and intelligent auto-scaling based on traffic patterns and performance metrics.

#### Create Multi-AZ Application Load Balancer
```bash
# Create Application Load Balancer with multi-AZ support
aws elbv2 create-load-balancer \
    --name nvc-banking-alb \
    --subnets subnet-xxxxxxxx subnet-yyyyyyyy \
    --security-groups sg-alb-xxxxxxxx \
    --scheme internet-facing \
    --type application \
    --ip-address-type ipv4 \
    --tags Key=Name,Value=nvc-banking-alb Key=Environment,Value=production

# Create target groups for different services
# Main application target group
aws elbv2 create-target-group \
    --name nvc-banking-app-targets \
    --protocol HTTPS \
    --port 443 \
    --vpc-id vpc-xxxxxxxx \
    --health-check-enabled \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --health-check-matcher HttpCode=200 \
    --target-type instance

# API target group for banking services
aws elbv2 create-target-group \
    --name nvc-banking-api-targets \
    --protocol HTTPS \
    --port 443 \
    --vpc-id vpc-xxxxxxxx \
    --health-check-enabled \
    --health-check-path /api/v1/health \
    --health-check-interval-seconds 15 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 2 \
    --health-check-matcher HttpCode=200 \
    --target-type instance
```

#### Advanced Load Balancer Configuration
```bash
# Create HTTPS listener with SSL termination
aws elbv2 create-listener \
    --load-balancer-arn arn:aws:elasticloadbalancing:us-east-2:123456789012:loadbalancer/app/nvc-banking-alb/1234567890abcdef \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=arn:aws:acm:us-east-2:123456789012:certificate/12345678-1234-1234-1234-123456789012 \
    --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/nvc-banking-app-targets/1234567890abcdef

# Create HTTP to HTTPS redirect listener
aws elbv2 create-listener \
    --load-balancer-arn arn:aws:elasticloadbalancing:us-east-2:123456789012:loadbalancer/app/nvc-banking-alb/1234567890abcdef \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=redirect,RedirectConfig='{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}'

# Create API routing rule
aws elbv2 create-rule \
    --listener-arn arn:aws:elasticloadbalancing:us-east-2:123456789012:listener/app/nvc-banking-alb/1234567890abcdef/1234567890abcdef \
    --priority 100 \
    --conditions Field=host-header,Values=api.nvcfund.com \
    --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/nvc-banking-api-targets/1234567890abcdef
```

### 2. Intelligent Auto Scaling Configuration

#### Launch Template for T3.micro Instances
```bash
# Create optimized launch template
aws ec2 create-launch-template \
    --launch-template-name nvc-banking-t3-template \
    --launch-template-data '{
        "ImageId": "ami-0c02fb55956c7d316",
        "InstanceType": "t3.micro",
        "KeyName": "nvc-banking-keypair",
        "SecurityGroupIds": ["sg-web-xxxxxxxx"],
        "IamInstanceProfile": {
            "Name": "nvc-banking-ec2-profile"
        },
        "UserData": "'$(base64 -w 0 user-data-optimized.sh)'",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "VolumeSize": 20,
                    "VolumeType": "gp3",
                    "Iops": 3000,
                    "Throughput": 125,
                    "Encrypted": true,
                    "DeleteOnTermination": true
                }
            }
        ],
        "MetadataOptions": {
            "HttpTokens": "required",
            "HttpPutResponseHopLimit": 1,
            "HttpEndpoint": "enabled"
        },
        "TagSpecifications": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "nvc-banking-web-server"},
                    {"Key": "Environment", "Value": "production"},
                    {"Key": "Application", "Value": "nvc-banking"},
                    {"Key": "AutoScaling", "Value": "enabled"}
                ]
            }
        ]
    }'
```

#### Multi-Tier Auto Scaling Groups
```bash
# Create primary Auto Scaling Group
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name nvc-banking-primary-asg \
    --launch-template LaunchTemplateName=nvc-banking-t3-template,Version='$Latest' \
    --min-size 2 \
    --max-size 10 \
    --desired-capacity 2 \
    --vpc-zone-identifier subnet-xxxxxxxx,subnet-yyyyyyyy \
    --target-group-arns arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/nvc-banking-app-targets/1234567890abcdef \
    --health-check-type ELB \
    --health-check-grace-period 300 \
    --default-cooldown 300 \
    --tags Key=Name,Value=nvc-banking-primary-asg,PropagateAtLaunch=true,ResourceId=nvc-banking-primary-asg,ResourceType=auto-scaling-group

# Create API-specific Auto Scaling Group
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name nvc-banking-api-asg \
    --launch-template LaunchTemplateName=nvc-banking-t3-template,Version='$Latest' \
    --min-size 1 \
    --max-size 5 \
    --desired-capacity 1 \
    --vpc-zone-identifier subnet-xxxxxxxx,subnet-yyyyyyyy \
    --target-group-arns arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/nvc-banking-api-targets/1234567890abcdef \
    --health-check-type ELB \
    --health-check-grace-period 300 \
    --default-cooldown 300 \
    --tags Key=Name,Value=nvc-banking-api-asg,PropagateAtLaunch=true,ResourceId=nvc-banking-api-asg,ResourceType=auto-scaling-group
```

### 3. Advanced Scaling Policies

#### CPU-Based Scaling
```bash
# Scale up policy for primary ASG
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name nvc-banking-primary-asg \
    --policy-name nvc-banking-scale-up-cpu \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "ScaleOutCooldown": 300,
        "ScaleInCooldown": 300
    }'

# Scale up policy for API ASG
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name nvc-banking-api-asg \
    --policy-name nvc-banking-api-scale-up-cpu \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "TargetValue": 60.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "ScaleOutCooldown": 180,
        "ScaleInCooldown": 300
    }'
```

#### Request-Based Scaling
```bash
# Request count scaling for high-traffic periods
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name nvc-banking-primary-asg \
    --policy-name nvc-banking-scale-up-requests \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "TargetValue": 1000.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ALBRequestCountPerTarget",
            "ResourceLabel": "app/nvc-banking-alb/1234567890abcdef/targetgroup/nvc-banking-app-targets/1234567890abcdef"
        },
        "ScaleOutCooldown": 300,
        "ScaleInCooldown": 300
    }'
```

#### Custom Metrics Scaling
```bash
# Database connection pool scaling
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/nvc-banking-cluster/nvc-banking-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 2 \
    --max-capacity 10

aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --resource-id service/nvc-banking-cluster/nvc-banking-service \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-name nvcfund-db-connections-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 80.0,
        "CustomizedMetricSpecification": {
            "MetricName": "DatabaseConnections",
            "Namespace": "NVC/Banking",
            "Statistic": "Average"
        },
        "ScaleOutCooldown": 300,
        "ScaleInCooldown": 600
    }'
```

### 4. Load Balancer Security & Performance Optimizations

#### Security Group for ALB
```bash
# Create dedicated security group for ALB
aws ec2 create-security-group \
    --group-name nvc-banking-alb-sg \
    --description "Security group for NVC Banking ALB" \
    --vpc-id vpc-xxxxxxxx

# Allow HTTPS from internet
aws ec2 authorize-security-group-ingress \
    --group-id sg-alb-xxxxxxxx \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Allow HTTP for redirect
aws ec2 authorize-security-group-ingress \
    --group-id sg-alb-xxxxxxxx \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Update web server security group to only allow ALB traffic
aws ec2 authorize-security-group-ingress \
    --group-id sg-web-xxxxxxxx \
    --protocol tcp \
    --port 80 \
    --source-group sg-alb-xxxxxxxx

aws ec2 authorize-security-group-ingress \
    --group-id sg-web-xxxxxxxx \
    --protocol tcp \
    --port 443 \
    --source-group sg-alb-xxxxxxxx
```

#### WAF Integration for Banking Security
```bash
# Create WAF for banking application
aws wafv2 create-web-acl \
    --scope REGIONAL \
    --name nvc-banking-waf \
    --default-action Allow={} \
    --description "WAF for NVC Banking Platform" \
    --rules '[
        {
            "Name": "AWSManagedRulesCommonRuleSet",
            "Priority": 1,
            "OverrideAction": {"None": {}},
            "VisibilityConfig": {
                "SampledRequestsEnabled": true,
                "CloudWatchMetricsEnabled": true,
                "MetricName": "CommonRuleSetMetric"
            },
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesCommonRuleSet"
                }
            }
        },
        {
            "Name": "BankingRateLimitRule",
            "Priority": 2,
            "Action": {"Block": {}},
            "VisibilityConfig": {
                "SampledRequestsEnabled": true,
                "CloudWatchMetricsEnabled": true,
                "MetricName": "BankingRateLimitMetric"
            },
            "Statement": {
                "RateBasedStatement": {
                    "Limit": 2000,
                    "AggregateKeyType": "IP"
                }
            }
        }
    ]'

# Associate WAF with ALB
aws wafv2 associate-web-acl \
    --web-acl-arn arn:aws:wafv2:us-east-2:123456789012:regional/webacl/nvc-banking-waf/12345678-1234-1234-1234-123456789012 \
    --resource-arn arn:aws:elasticloadbalancing:us-east-2:123456789012:loadbalancer/app/nvc-banking-alb/1234567890abcdef
```

### 5. Performance Optimizations
```python
# Add to gunicorn configuration
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

## AWS Console GUI Guide

### Comprehensive AWS Management Console Instructions
This section provides step-by-step GUI instructions for setting up the NVC Banking Platform infrastructure using the AWS Management Console, complementing the CLI scripts provided above.

### 1. VPC and Networking Setup (GUI)

#### Creating VPC
1. **Navigate to VPC Dashboard**
   - Go to AWS Console → Services → VPC
   - Click "Create VPC"

2. **VPC Configuration**
   ```
   VPC Settings:
   - Resources to create: VPC and more
   - Name tag: nvc-banking-vpc
   - IPv4 CIDR block: 10.0.0.0/16
   - IPv6 CIDR block: No IPv6 CIDR block
   - Tenancy: Default
   
   Subnets:
   - Number of Availability Zones: 2
   - Number of public subnets: 2
   - Number of private subnets: 2
   - Public subnet CIDR blocks: 10.0.1.0/24, 10.0.2.0/24
   - Private subnet CIDR blocks: 10.0.3.0/24, 10.0.4.0/24
   
   NAT Gateways: 1 per AZ
   VPC Endpoints: None
   DNS Options: Enable DNS hostnames and resolution
   ```

3. **Review and Create**
   - Review configuration
   - Click "Create VPC"
   - Wait for completion (approximately 2-3 minutes)

### 2. Auto Scaling Group Setup via Console

#### Launch Template Creation
1. **Navigate to EC2 Console**
   - AWS Console → Services → EC2 → Launch Templates
   - Click "Create launch template"

2. **Launch Template Configuration**
   ```
   Launch template name: nvc-banking-t3-template
   Template version description: T3.micro template for NVC Banking
   
   Application and OS Images:
   - AMI: Ubuntu Server 22.04 LTS (ami-0c02fb55956c7d316)
   
   Instance type: t3.micro (upgraded from t2.micro)
   
   Key pair: nvc-banking-keypair (create if doesn't exist)
   
   Network settings:
   - Subnet: Don't include in launch template
   - Security groups: nvc-banking-web-sg
   
   Storage:
   - Volume 1: 20 GiB, gp3, Encrypted
   
   Advanced details:
   - IAM instance profile: nvc-banking-ec2-profile
   - User data: [Your application startup script]
   ```

#### Auto Scaling Group Setup
1. **Create Auto Scaling Group**
   - EC2 Console → Auto Scaling Groups → Create Auto Scaling group

2. **ASG Configuration**
   ```
   Choose launch template:
   - Auto Scaling group name: nvc-banking-primary-asg
   - Launch template: nvc-banking-t3-template
   - Version: Latest
   
   Network:
   - VPC: nvc-banking-vpc
   - Subnets: Select public subnets (us-east-2a, us-east-2b)
   
   Load balancing:
   - Attach to a new load balancer
   - Load balancer type: Application Load Balancer
   - Load balancer name: nvc-banking-alb
   - Load balancer scheme: Internet-facing
   - Network mapping: Select public subnets
   
   Health checks:
   - ELB health checks: Enable
   - Health check grace period: 300 seconds
   
   Group size:
   - Desired capacity: 2
   - Minimum capacity: 2
   - Maximum capacity: 10
   
   Scaling policies:
   - Target tracking scaling policy
   - Metric type: Average CPU utilization
   - Target value: 70%
   ```

### 3. Route 53 DNS Configuration for nvcfund.com

#### Hosted Zone Setup
1. **Navigate to Route 53**
   - AWS Console → Route 53 → Hosted zones
   - Click "Create hosted zone"

2. **Hosted Zone Configuration**
   ```
   Domain name: nvcfund.com
   Description: NVC Fund Banking Platform DNS
   Type: Public hosted zone
   
   Tags:
   - Environment: production
   - Application: nvc-banking
   ```

3. **Update Hostgator Name Servers**
   - After creation, copy the 4 name servers from Route 53
   - Login to Hostgator control panel
   - Update domain name servers to AWS Route 53 name servers

#### DNS Records Creation
1. **A Record for Main Domain**
   ```
   Record name: [blank] (for nvcfund.com)
   Record type: A
   Alias: Yes
   Route traffic to: Application and Classic Load Balancer
   Region: US East (N. Virginia)
   Load balancer: nvc-banking-alb
   ```

2. **CNAME Record for WWW**
   ```
   Record name: www
   Record type: CNAME
   Value: nvcfund.com
   TTL: 300
   ```

3. **A Record for API Subdomain**
   ```
   Record name: api
   Record type: A
   Alias: Yes
   Route traffic to: Application and Classic Load Balancer
   Region: US East (N. Virginia)
   Load balancer: nvc-banking-alb
   ```

### 4. Secrets Manager for Boto3 Integration

#### Database Secrets (Already Configured)
Since your EC2 instance already uses Boto3 for secrets management, ensure these secrets exist:

1. **Navigate to Secrets Manager**
   - AWS Console → Secrets Manager → Store a new secret

2. **Database Secret Configuration**
   ```
   Secret type: Credentials for RDS database
   Database: nvcfund-db
   
   Credentials:
   - User name: nvcdba
   - Password: [Auto-generated or custom]
   
   Secret name: nvc-banking/database
   Description: Database credentials for NVC Banking Platform
   
   Automatic rotation: Configure automatic rotation
   Rotation interval: 30 days
   ```

3. **Application Secrets**
   ```
   Secret type: Other type of secret
   
   Key/value pairs:
   - SESSION_SECRET: [Generate strong secret]
   - DATABASE_URL: postgresql://nvcdba:password@rds-endpoint:5432/nvcfund_db
   - MAIL_USERNAME: your-email@gmail.com
   - MAIL_PASSWORD: your-app-password
   
   Secret name: nvc-banking/application
   ```

### 5. Load Balancer Configuration (GUI)

#### ALB Creation
1. **Navigate to Load Balancers**
   - EC2 Console → Load Balancers → Create Load Balancer
   - Choose "Application Load Balancer"

2. **ALB Configuration**
   ```
   Basic configuration:
   - Name: nvc-banking-alb
   - Scheme: Internet-facing
   - IP address type: IPv4
   
   Network mapping:
   - VPC: nvc-banking-vpc
   - Mappings: us-east-2a (public subnet), us-east-2b (public subnet)
   
   Security groups:
   - nvc-banking-alb-sg
   
   Listeners and routing:
   - Protocol: HTTPS, Port: 443
   - Default action: Forward to target group
   - Target group: Create new target group
   
   Target group configuration:
   - Target group name: nvc-banking-app-targets
   - Protocol: HTTP, Port: 80
   - VPC: nvc-banking-vpc
   - Health check path: /health
   ```

#### Advanced Scaling Configuration
1. **Create Multiple Target Groups**
   ```
   Main Application Target Group:
   - Name: nvc-banking-app-targets
   - Protocol: HTTP, Port: 80
   - Health check: /health
   
   API Target Group:
   - Name: nvc-banking-api-targets  
   - Protocol: HTTP, Port: 80
   - Health check: /api/v1/health
   ```

2. **Listener Rules for Domain Routing**
   ```
   Rule 1: API Subdomain
   - Conditions: Host header = api.nvcfund.com
   - Actions: Forward to nvc-banking-api-targets
   - Priority: 100
   
   Rule 2: Main Domain (Default)
   - Conditions: Default
   - Actions: Forward to nvc-banking-app-targets
   ```

### 6. Certificate Manager Integration

#### SSL Certificate for nvcfund.com
1. **Certificate Manager**
   - AWS Console → Certificate Manager → Request certificate
   
2. **Certificate Configuration**
   ```
   Certificate type: Request a public certificate
   
   Domain names:
   - nvcfund.com
   - www.nvcfund.com
   - api.nvcfund.com
   
   Validation method: DNS validation
   Key algorithm: RSA 2048
   ```

3. **DNS Validation**
   - Add CNAME records to Route 53 for validation
   - ACM will automatically validate via Route 53

### 7. CloudWatch Monitoring Dashboard

#### Create Production Dashboard
1. **CloudWatch Console**
   - AWS Console → CloudWatch → Dashboards
   - Create dashboard: "NVC-Banking-Production"

2. **Essential Widgets**
   ```
   EC2 Auto Scaling Metrics:
   - CPUUtilization by Auto Scaling Group
   - NetworkIn/NetworkOut
   - Instance count
   
   Application Load Balancer Metrics:
   - RequestCount
   - TargetResponseTime
   - HTTPCode_Target_2XX_Count
   - HTTPCode_Target_4XX_Count
   - HTTPCode_Target_5XX_Count
   
   RDS Database Metrics:
   - CPUUtilization
   - DatabaseConnections
   - ReadLatency/WriteLatency
   - FreeableMemory
   
   Custom Application Metrics:
   - Banking transaction volume
   - User authentication rate
   - API response times
   ```

### 8. Security Configuration

#### WAF Setup for Banking Security
1. **WAF Console**
   - AWS Console → WAF & Shield → Web ACLs
   - Create web ACL

2. **Banking-Specific Rules**
   ```
   Web ACL Configuration:
   - Name: nvc-banking-waf
   - Resource type: Application Load Balancer
   - Associated resources: nvc-banking-alb
   
   Rule Sets:
   1. AWS Managed Rules - Core rule set
   2. AWS Managed Rules - Known bad inputs  
   3. AWS Managed Rules - SQL injection
   4. Rate limiting: 2000 requests per 5 minutes
   5. Geographic blocking (if required)
   
   Custom Rules for Banking:
   - Block requests without proper authentication headers
   - Rate limit login attempts
   - Monitor for suspicious transaction patterns
   ```

### 9. Instance Migration: T2 to T3 Micro

#### Seamless Migration via Console
1. **Current Instance Assessment**
   - EC2 Console → Instances
   - Select your current T2.micro instance
   - Note Instance ID, Security Groups, and Subnet

2. **Create AMI Backup**
   - Right-click instance → Image and templates → Create image
   - Image name: nvc-banking-t2-backup-YYYYMMDD
   - No reboot: Uncheck for data consistency

3. **Migration Options**

   **Option A: Stop and Modify (Brief Downtime)**
   - Stop the instance
   - Actions → Instance settings → Change instance type
   - New instance type: t3.micro
   - Start the instance

   **Option B: Blue-Green Deployment (Zero Downtime)**
   - Launch new T3.micro instance
   - Deploy application to new instance
   - Update load balancer targets
   - Deregister old instance

### 10. Performance Optimization Settings

#### Auto Scaling Optimization
1. **Scaling Policies Configuration**
   ```
   Target Tracking Policies:
   - CPU Utilization: 70% target
   - Request Count: 1000 requests per target
   - Custom metrics: Database connections
   
   Step Scaling Policies:
   - Scale out: +2 instances when CPU > 80%
   - Scale in: -1 instance when CPU < 40%
   
   Scheduled Scaling:
   - Business hours: Min 4, Max 12 instances
   - Off hours: Min 2, Max 6 instances
   ```

2. **Health Check Optimization**
   ```
   ELB Health Checks:
   - Health check path: /health
   - Healthy threshold: 2
   - Unhealthy threshold: 3
   - Timeout: 5 seconds
   - Interval: 30 seconds
   
   Auto Scaling Health Checks:
   - Health check type: ELB
   - Health check grace period: 300 seconds
   ```

This comprehensive GUI guide ensures you can manage the entire NVC Banking Platform infrastructure through the AWS Console, providing visual confirmation of configurations and easier management for non-CLI users.

## Troubleshooting

### Common Issues and Solutions

1. **Database Connection Issues**
```bash
# Check RDS connectivity
telnet nvcfund-db.cluster-xxxxx.us-east-2.rds.amazonaws.com 5432

# Check security groups
aws ec2 describe-security-groups --group-ids sg-rds-xxxxxxxx

# Test database connection
python3 -c "import psycopg2; conn = psycopg2.connect('$DATABASE_URL'); print('Connected successfully')"
```

2. **Application Deployment Issues**
```bash
# Check application logs
journalctl -u nvc-banking -f

# Check Nginx configuration
nginx -t
systemctl status nginx

# Check disk space
df -h
```

3. **Performance Issues**
```bash
# Monitor system resources
htop
iostat -x 1

# Check application metrics
curl http://localhost:5000/health

# Monitor database performance
aws rds describe-db-instances --db-instance-identifier nvcfund-db
```

4. **SSL Certificate Issues**
```bash
# Check certificate status
certbot certificates

# Test SSL configuration
openssl s_client -connect your-domain.com:443

# Renew certificate
certbot renew --dry-run
```

### Rollback Procedures

1. **Application Rollback**
```bash
# Rollback to previous version
cd /home/nvcapp/nvc-banking-platform
git log --oneline -10
git checkout <previous-commit-hash>
systemctl restart nvc-banking
```

2. **Database Rollback**
```bash
# Restore from RDS snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier nvcfund-db-restored \
    --db-snapshot-identifier nvcfund-db-snapshot-2025-01-01
```

3. **Frontend Rollback**
```bash
# Rollback S3 deployment
aws s3 sync s3://nvc-banking-frontend-backup/ s3://nvc-banking-frontend-prod/ --delete
aws cloudfront create-invalidation --distribution-id E1234567890ABC --paths "/*"
```

## Cost Optimization

### 1. Reserved Instances
```bash
# Purchase Reserved Instances for predictable workloads
aws ec2 describe-reserved-instances-offerings \
    --instance-type t3.medium \
    --product-description "Linux/UNIX"
```

### 2. S3 Lifecycle Policies
```json
{
    "Rules": [
        {
            "Id": "NVCBankingLogArchival",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "logs/"
            },
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                },
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ]
        }
    ]
}
```

### 3. Monitoring and Alerts
```bash
# Create billing alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "NVC-Banking-Billing-Alarm" \
    --alarm-description "Billing alarm for NVC Banking Platform" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 86400 \
    --threshold 1000 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=Currency,Value=USD \
    --evaluation-periods 1
```

## Final Deployment Checklist

- [ ] VPC and networking configured
- [ ] Security groups properly configured
- [ ] RDS PostgreSQL instance created and accessible
- [ ] EC2 instances launched with proper IAM roles
- [ ] Application deployed and running
- [ ] Nginx configured with SSL certificates
- [ ] Frontend deployed to S3 and CloudFront
- [ ] Secrets properly configured in AWS Secrets Manager
- [ ] Monitoring and logging configured
- [ ] Auto Scaling Group configured
- [ ] Load balancer configured and health checks passing
- [ ] Domain name configured with Route 53
- [ ] Backup procedures in place
- [ ] Security audit completed
- [ ] Performance testing completed
- [ ] Disaster recovery plan documented

---

This comprehensive AWS deployment guide ensures your NVC Banking Platform is deployed with enterprise-grade security, scalability, and reliability. For additional support or customization, consult your DevOps team or AWS support.
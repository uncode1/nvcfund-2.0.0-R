# NVC Banking Platform - Standard Python Server Deployment Guide

## Overview

This guide provides instructions for deploying the NVC Banking Platform on any standard Python server environment, following normal Python deployment principles.

> **For AWS Enterprise Deployment**: See [AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md) for high-availability cloud infrastructure.

> **Quick Checklist**: See [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) for pre-deployment verification.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Redis (optional, for enhanced session storage)
- SSL certificate for HTTPS

## Environment Variables

The application requires the following environment variables for production:

### Required Variables
```bash
# Security
SECRET_KEY=your-secret-key-here
SESSION_SECRET=your-session-secret-here

# Database
DATABASE_URL=postgresql://username:password@host:port/database_name

# Application Environment
FLASK_ENV=production
FLASK_APP=nvcfund-backend.app_factory:create_app

# Security Configuration
BEHIND_PROXY=true  # Set to true if behind nginx/apache proxy

# Rate Limiting (Optional - defaults provided)
RATELIMIT_DEFAULT=100 per hour  # Per-user rate limit in production
RATELIMIT_STORAGE_URI=memory://  # Rate limit storage backend
```

### Optional Variables
```bash
# CORS Configuration (comma-separated)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email Configuration
MAIL_SERVER=smtp.your-provider.com
MAIL_PORT=587
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-email-password
MAIL_USE_TLS=true

# External API Keys
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET_KEY=your-binance-secret-key
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
SENDGRID_API_KEY=your-sendgrid-api-key
```

## Installation Steps

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd nvcfund

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r pyproject.toml
```

### 2. Database Setup
```bash
# Create PostgreSQL database
createdb nvc_banking_prod

# Set environment variables
export DATABASE_URL="postgresql://username:password@localhost:5432/nvc_banking_prod"

# Initialize database (automatic on first run)
```

### 3. Application Configuration

Create a production environment file `.env`:
```bash
SECRET_KEY=your-secret-key-here
SESSION_SECRET=your-session-secret-here
DATABASE_URL=postgresql://username:password@localhost:5432/nvc_banking_prod
FLASK_ENV=production
BEHIND_PROXY=true
CORS_ORIGINS=https://yourdomain.com
```

### 4. Run with Gunicorn

#### Development Testing
```bash
cd nvcfund-backend
python -m flask --app app_factory:create_app run --host=0.0.0.0 --port=5000
```

#### Production Deployment
```bash
# Using the included gunicorn configuration
gunicorn --config gunicorn.conf.py nvcfund_backend.wsgi:application

# Or with custom parameters
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 nvcfund_backend.wsgi:application
```

## Nginx Configuration

Example nginx configuration for production:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /path/to/your/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Production Security Features

### Core Security
- Banking-grade password complexity (12+ characters, mixed requirements)
- Session management with 15-minute timeout in production
- CSRF protection with 1-hour token lifetime
- Role-based access control (RBAC) with granular permissions
- Comprehensive audit logging for compliance

### Rate Limiting & Abuse Prevention
- **Per-user rate limiting**: 100 requests/hour per authenticated user
- **IP-based protection**: Automatic blocking for abuse patterns  
- **Progressive penalties**: 15-minute blocks for limit violations
- **Banking-specific limits**: Enhanced protection for financial operations

### Session & Authentication Security
- **Session Timeouts by Environment**:
  - Production: 15 minutes (banking compliance)
  - Development: 24 hours (convenience)
  - Testing: 30 minutes
- **Multi-Factor Authentication**: Optional MFA for sensitive operations
- **Secure cookies**: HttpOnly, Secure, SameSite=Lax in production

## Production Security Checklist

- [ ] Set strong SECRET_KEY and SESSION_SECRET
- [ ] Configure HTTPS with valid SSL certificate
- [ ] Set BEHIND_PROXY=true when behind reverse proxy
- [ ] Configure restrictive CORS_ORIGINS
- [ ] Use strong database credentials
- [ ] Verify rate limiting configuration (100/hour per user)
- [ ] Set up firewall rules
- [ ] Configure log rotation
- [ ] Set up monitoring and alerting
- [ ] Regular security updates

## File Structure

The application follows standard Python packaging:
```
nvcfund/
├── nvcfund-backend/          # Main application package
│   ├── modules/              # Modular components
│   ├── static/               # Static files
│   ├── templates/            # Jinja2 templates
│   ├── app_factory.py        # Application factory
│   ├── config.py             # Configuration classes
│   └── wsgi.py               # WSGI entry point
├── gunicorn.conf.py          # Gunicorn configuration
├── main.py                   # Entry point for development
└── pyproject.toml            # Dependencies
```

## Standard Python Environment Compliance

This application follows standard Python deployment practices:

- Uses environment variables for configuration
- Includes proper WSGI entry point
- Compatible with standard WSGI servers (Gunicorn, uWSGI, etc.)
- No platform-specific dependencies
- Standard logging configuration
- Production/development configuration separation
- Standard project structure

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure PYTHONPATH includes the application directory
2. **Database Errors**: Verify DATABASE_URL format and database accessibility
3. **Permission Errors**: Check file permissions and user privileges
4. **SSL Errors**: Verify certificate paths and validity

### Logs

Application logs are available in:
- Console output (when running with Gunicorn)
- File logs in `logs/` directory (created automatically)
- System logs via systemd (if configured)

### Performance Tuning

- Adjust Gunicorn worker count based on CPU cores
- Configure database connection pooling
- Implement Redis for session storage (optional)
- Set up CDN for static files
- Configure caching headers

## Related Documentation

- **[AWS Enterprise Deployment](./AWS_DEPLOYMENT_GUIDE.md)** - High availability cloud infrastructure
- **[Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)** - Pre-deployment verification
- **[Operations Runbook](./OPERATIONS_RUNBOOK.md)** - Daily operations and maintenance
- **[Developer Guide](./DEVELOPER_GUIDE.md)** - Development environment setup

## Support

For deployment issues, check:
1. Environment variable configuration
2. Database connectivity
3. File permissions
4. Network accessibility
5. SSL certificate validity

For development and architecture questions, refer to the [Developer Guide](./DEVELOPER_GUIDE.md).
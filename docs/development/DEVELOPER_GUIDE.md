# NVC Banking Platform - Developer Guide

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Development Environment Setup](#development-environment-setup)
4. [UI Development](#ui-development)
5. [Modular Architecture](#modular-architecture)
6. [Database Schema](#database-schema)
7. [API Documentation](#api-documentation)
8. [Testing Guide](#testing-guide)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

## Overview

The NVC Banking Platform is a comprehensive enterprise-grade banking application built with modern technologies and banking-grade security. It features a pure modular architecture with 34+ specialized financial service modules.

### Technology Stack
- **Backend**: Flask 3.0+ with Python 3.11+
- **Frontend**: React 18.3.1 with TypeScript
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0+
- **Security**: Banking-grade encryption and compliance frameworks
 
## UI Development

The NVC Banking Platform utilizes a decoupled frontend-backend architecture. The frontend is a modern Single-Page Application (SPA) built with **React 18.3.1 and TypeScript**.

All user interfaces are managed by the React application, which communicates with the Flask backend via a comprehensive JSON API. The backend is purely an API service and does not render any HTML templates.

## Development Environment Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ with npm
- PostgreSQL 15+
- Redis 6+
- Git

### Backend Setup
1. **Clone and Setup Environment**
   ```bash
   git clone <repository>
   cd nvcfund-backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**

   **⚠️ Important**: This application uses vault-managed credentials. No credentials should be hardcoded.

   ```bash
   # Required environment variables (managed by vault):
   export DATABASE_URL="postgresql://user:password@localhost/nvcbank"
   export SESSION_SECRET="your-vault-managed-secret"
   export FLASK_ENV="development"

   # For local development, you can temporarily set these manually:
   # (DO NOT commit these values to version control)
   ```

   **Vault Integration Examples:**
   ```bash
   # HashiCorp Vault
   export DATABASE_URL=$(vault kv get -field=database_url secret/nvc-banking/dev)
   export SESSION_SECRET=$(vault kv get -field=session_secret secret/nvc-banking/dev)

   # AWS Secrets Manager
   export DATABASE_URL=$(aws secretsmanager get-secret-value --secret-id nvc-banking/dev/database --query SecretString --output text | jq -r .database_url)

   # Azure Key Vault
   export DATABASE_URL=$(az keyvault secret show --vault-name nvc-banking-vault --name database-url --query value -o tsv)
   ```

4. **Database Setup**
   ```bash
   # Create database
   createdb nvcbank
   
   # Run migrations
   python -c "from app_factory import create_app; from modules.core.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

5. **Run Development Server**
   ```bash
   python main.py
   # or
   gunicorn --bind 0.0.0.0:5000 --reload main:app
   ```

### Frontend Setup
1. **Navigate to Frontend**
   ```bash
   cd nvcfund-frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Environment Configuration**
   ```bash
   # Create .env file
   REACT_APP_API_URL=http://localhost:5000
   REACT_APP_ENVIRONMENT=development
   ```

4. **Run Development Server**
   ```bash
   npm start
   ```

## Authentication & Security

### Password Complexity Requirements
The platform enforces banking-grade password complexity:
- **Minimum 12 characters** length
- **At least 2 uppercase** letters
- **At least 2 lowercase** letters  
- **At least 2 numbers**
- **At least 2 special characters** (!@#$%^&*(),.?":{}|<>)
- **No common patterns** (password, admin, banking, etc.)
- **Maximum 2 repeated characters**
- **No consecutive sequences** (abc, 123, etc.)
- **Minimum 8 unique characters**

### Test Credentials
For development testing:
```
Username: uncode
Password: Zx9Wq2@#ComplexCeo
Role: super_admin

Username: regular_user  
Password: Ky5Rp8!$StandardUsr9
Role: USER

Username: demo_user
Password: Nz4Wq7@&SecureDmoTst
Role: USER
```

### Role-Based Access Control (RBAC)
- **super_admin**: Full system access
- **admin**: Administrative functions
- **treasury_officer**: Treasury operations
- **compliance_officer**: Compliance functions
- **USER**: Standard banking operations

## Comprehensive Data Security Framework

### Data Protection Architecture
The NVC Banking Platform implements banking-grade data security with comprehensive protection for both data in transit and data at rest across all application functions and modules.

### Core Security Components

#### 1. Data at Rest Protection
```python
# Automatic field-level encryption using secure mixins
from modules.security_center.secure_models import BankingAccountSecureMixin

class BankAccount(BankingAccountSecureMixin, db.Model):
    # Sensitive fields automatically encrypted
    def set_account_number(self, account_number):
        # Automatically encrypted with AES-256
        super().set_account_number(account_number)
    
    def get_masked_account_number(self):
        # Returns: ************1234
        return super().get_masked_account_number()
```

#### 2. Data in Transit Protection
```python
# Secure route decorators for banking-grade protection
from modules.security_center.secure_routes import banking_grade_security, secure_data_transmission

@banking_bp.route('/transfer', methods=['POST'])
@banking_grade_security(require_mfa=True, audit_level='detailed')
@secure_data_transmission(require_encryption=True)
def secure_transfer():
    # Request data automatically decrypted and validated
    # Response data automatically encrypted before transmission
    pass
```

#### 3. Encryption Standards
- **AES-256 encryption** for all sensitive data at rest
- **PBKDF2 with 100,000 iterations** for password hashing
- **HMAC-SHA256** for data integrity verification
- **End-to-end payload encryption** for data in transit
- **Cryptographically secure token generation**

#### 4. Secure Model Mixins
```python
# Available secure mixins for different data types
from modules.security_center.secure_models import (
    SecureFieldMixin,           # Base security functionality
    BankingAccountSecureMixin,  # Banking account data
    UserSecureMixin,           # User personal information
    TransactionSecureMixin     # Transaction data
)

class User(UserSecureMixin, db.Model):
    # Email, phone, address automatically encrypted
    def set_email(self, email):
        # Automatically encrypted
        super().set_email(email)
    
    def get_masked_email(self):
        # Returns: u***@example.com
        return super().get_masked_email()
```

#### 5. Security Validation
```python
# Comprehensive security testing and validation
from modules.security_center.data_security_implementation import (
    validate_platform_security,
    generate_security_report
)

# Validate all security measures
security_status = validate_platform_security()

# Generate compliance report
security_report = generate_security_report()
```

### Implementation Guidelines

#### Module Security Integration
```python
# Apply security to new modules
from modules.security_center.data_security_implementation import apply_module_security

# Automatically applies appropriate security measures
security_config = apply_module_security('your_module_name')
```

#### Environment Setup
```bash
# Required environment variable for production
export DATA_ENCRYPTION_KEY="base64-encoded-encryption-key"

# Generate secure encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Security Compliance
- **GDPR Compliance**: Personal data protection and encryption
- **PCI-DSS Compliance**: Credit card data encryption standards
- **SOX Compliance**: Financial data integrity and audit trails
- **Basel III Compliance**: Risk management data protection
- **Banking Regulations**: Multi-layer security enforcement

## Modular Architecture

### Core Modules
1. **auth** - Authentication and user management
2. **banking** - Core banking operations
3. **treasury** - Treasury management and liquidity
4. **compliance** - Regulatory compliance and reporting
5. **analytics** - Financial analytics and business intelligence

### Module Structure
```
modules/module_name/
├── __init__.py          # Blueprint registration
├── routes.py            # Route handlers
├── models.py            # Database models
├── services.py          # Business logic
├── api.py               # API endpoints (often merged into routes.py)
└── static/            # Module assets
```

### Creating New Modules
```bash
# Create module structure
mkdir -p modules/new_module/{templates/new_module,static}
touch modules/new_module/{__init__.py,routes.py,models.py,services.py}
```

## Database Schema

### Migration System
The platform uses automatic database migrations via `modules/core/database_migration.py`:

```python
# Apply migrations
from modules.core.database_migration import DatabaseMigration
migration = DatabaseMigration()
migration.check_and_apply_migrations()
```

### Key Models
- **User**: Core user authentication and profile
- **KYCVerification**: KYC document verification
- **BankAccount**: Banking account management
- **Transaction**: Financial transaction records

## API Documentation

### Authentication Endpoints
```http
POST /auth/login
POST /auth/logout
POST /auth/register
GET  /auth/profile
```

### Banking Operations
```http
GET  /banking/accounts
POST /banking/accounts
GET  /banking/transactions
POST /banking/transfer
```

### Treasury Operations
```http
GET  /treasury/liquidity
POST /treasury/reserves
GET  /treasury/settlements
```

### API Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "timestamp": "2025-07-06T00:00:00Z"
}
```

## Testing Guide

### Test Structure
```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── api/              # API endpoint tests
└── ui/               # UI/template tests
```

### Running Tests
```bash
# All tests
pytest

# Specific module
pytest tests/unit/test_auth.py

# Coverage report
pytest --cov=modules
```

## Security Implementation

### Authentication Flow
1. User login with credentials
2. JWT token generation
3. Token validation on protected routes
4. Session management with Redis

### Security Headers
```python
# Implemented in unified_base.html
Content-Security-Policy: default-src 'self'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

## Performance Optimization

### Caching Strategy
- **Redis**: Session storage and API caching
- **Database**: Query optimization with indexes
- **Frontend**: Asset bundling and compression

### Monitoring
```bash
# System health
./scripts/monitor_cron_health.sh

# Security monitoring
tail -f logs/efficient_security_monitor.log
```

## Deployment

### Environment Setup
```bash
# Production deployment
python scripts/deploy_production.py

# Health check
python scripts/health_check.py
```

### Package Management
For complete package management procedures, see [Operations Documentation](../operations/README.md).

## Troubleshooting

### Common Issues
1. **Template Errors**: Use `template_consistency_checker.py`
2. **Database Issues**: Check migration logs
3. **API Errors**: Verify authentication headers
4. **Performance**: Monitor with system health scripts

### Debug Mode
```bash
# Enable debug logging
export FLASK_ENV=development
export FLASK_DEBUG=1
```

---

**For detailed UI development**: See [Unified UI Developer Guide](../DEVELOPER_GUIDE_UNIFIED_UI.md)
**For operations**: See [Operations Documentation](../operations/README.md)
**For compliance**: See [Compliance Documentation](../compliance/README.md)

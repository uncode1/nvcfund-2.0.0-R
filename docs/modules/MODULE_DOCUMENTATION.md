# NVC Banking Platform - Module Documentation

## Overview

The NVC Banking Platform is built using a pure modular architecture where each feature is self-contained within its own module. This document provides comprehensive documentation for all modules in the platform.

## Module Architecture

Each module follows a consistent structure:

```
modules/module_name/
├── __init__.py              # Module initialization and blueprint
├── routes.py                # Flask routes and view functions
├── models.py                # Database models
├── services.py              # Business logic and services
├── forms.py                 # WTForms for data validation
├── api/                     # API endpoints
│   ├── __init__.py
│   └── endpoints.py
```

## Core Platform Modules (Alphabetical)

### 1. Accounts Module (`accounts/`)

**Purpose**: Bank account management and operations

**Key Components:**
- Account creation and management
- Account balance tracking
- Account limits and controls
- Account statements and reporting

**Status**: Active module in platform

**API Endpoints:**
```
GET /api/v1/accounts/                  # Account overview
POST /api/v1/accounts/create           # Create new account
GET /api/v1/accounts/{id}/details     # Account details
```

### 2. Admin Management Module (`admin_management/`)

**Purpose**: System administration and management

**Key Components:**
- User lifecycle management
- System configuration management
- Security settings and policies
- Audit and monitoring tools
- Advanced features management

**Models:**
- System configuration tracking
- Admin action logging
- Module configuration management

**Key Routes:**
```python
/admin/                    # Admin dashboard
/admin/users              # User management
/admin/logs               # System logs
/admin/security           # Security monitoring
/admin/override           # System overrides
```

**Features:**
- AI fraud detection management
- Real-time analytics control
- Multi-currency support configuration
- Blockchain integration management
- Regulatory compliance monitoring

### 3. Authentication Module (`auth/`)

**Purpose**: User authentication, registration, and profile management

**Key Components:**
- User registration and login with enhanced security
- Password management and reset
- Profile management and KYC verification
- Session management with MFA support
- Role-based access control

**Models:**
- `User` - Core user model with authentication
- `KYCVerification` - KYC document verification
- `UserSession` - Session tracking
- `PasswordReset` - Password reset tokens

**Key Routes:**
```python
/auth/login              # User login
/auth/register           # User registration
/auth/logout             # User logout
/auth/profile            # Profile management
/auth/verify-kyc         # KYC verification
/auth/kyc/onboarding     # KYC onboarding process
```

**Security Features:**
- Enhanced security with centralized audit logging
- MFA system integration
- Account lockout protection
- CSRF protection and rate limiting

### 4. Banking Module (`banking/`)

**Purpose**: Core banking operations including accounts, transactions, and transfers

**Key Components:**
- Bank account management
- Transaction processing and history
- Money transfers (domestic and international)
- Balance tracking and management
- Account statements

**Models:**
- `BankAccount` - Bank account information
- `Transaction` - Transaction records
- `Transfer` - Money transfer operations
- `AccountBalance` - Balance tracking

**Key Routes:**
```python
/banking/accounts           # Account management
/banking/transactions       # Transaction history
/banking/transfer          # Money transfers
/banking/statements        # Account statements
```

### 5. Compliance Module (`compliance/`)

**Purpose**: Regulatory compliance, reporting, and audit trails

**Key Components:**
- Regulatory reporting automation
- Audit trail management
- Compliance monitoring and frameworks
- Risk assessment and scoring
- Document management and retention

**Models:**
- `ComplianceFramework` - Regulatory frameworks
- `ComplianceReport` - Compliance reports
- `AuditLog` - Audit trail records
- `RegulatoryRequirement` - Compliance requirements

**Key Routes:**
```python
/compliance/reports        # Compliance reporting
/compliance/audit         # Audit trail
/compliance/monitoring    # Compliance monitoring
/compliance/frameworks    # Regulatory frameworks
```

### 6. Core Module (`core/`)

**Purpose**: Shared utilities and core functionality

**Key Components:**
- Database utilities and configuration
- Security decorators and middleware
- Navigation utilities and RBAC
- Logging and monitoring systems
- Template management and module overview

**Key Files:**
- `database.py` - Database configuration
- `security.py` - Security utilities
- `rbac.py` - Role-based access control
- `modular_blueprint_registration.py` - Module registration
- `api_security.py` - API security management
- `enterprise_security.py` - Enterprise security features
- `gdpr_rights_manager.py` - GDPR compliance

**Templates:**
- `module_overview.html` - Module overview dashboard
- `module_categorization_dashboard.html` - Module categorization

### 7. Dashboard Module (`dashboard/`)

**Purpose**: User dashboard and summary information

**Key Components:**
- Account summaries and overviews
- Recent transaction displays
- Quick action buttons and specialized compliance
- Financial insights and KYC verification
- Personalized notifications

**Models:**
- `DashboardWidget` - Dashboard widget configurations
- `UserPreference` - User dashboard preferences
- `Notification` - User notifications

**Key Routes:**
```python
/dashboard/                           # Main dashboard
/dashboard/summary                    # Account summary
/dashboard/notifications              # User notifications
/dashboard/specialized-compliance/kyc-verification  # KYC verification
```

## Product Modules (Alphabetical)

### 8. Cards & Payments Module (`products/cards_payments/`)

**Purpose**: Card and payment processing services

**Key Components:**
- Card lifecycle management
- Payment processing and routing
- Fraud detection and prevention
- Merchant services

**Status**: Active product module

### 9. Insurance Module (`products/insurance/`)

**Purpose**: Insurance products and services

**Key Components:**
- Insurance policy management
- Claims processing
- Premium calculations
- Risk assessment

**Status**: Active product module

### 10. Investments Module (`products/investments/`)

**Purpose**: Investment products and portfolio management

**Key Components:**
- Investment product catalog
- Portfolio management
- Performance tracking
- Investment recommendations

**Status**: Active product module

### 11. Islamic Banking Module (`products/islamic_banking/`)

**Purpose**: Sharia-compliant financial products and services

**Key Components:**
- Sharia-compliant product management
- Islamic financing products (Murabaha, Ijara)
- Zakat calculation and management
- Sharia compliance monitoring

**Status**: Active product module

### 12. Loans Module (`products/loans/`)

**Purpose**: Loan products and management

**Key Components:**
- Loan application processing
- Credit assessment and scoring
- Loan disbursement and tracking
- Repayment management

**Status**: Active product module

### 13. Trading Module (`products/trading/`)

**Purpose**: Trading platform and investment services

**Key Components:**
- Trading account management
- Order processing and execution
- Market data integration
- Portfolio management and risk controls

**Models:**
- `TradingAccount` - Trading accounts
- `TradingOrder` - Trading orders
- `TradingInstrument` - Trading instruments
- `Portfolio` - Investment portfolios

**Key Routes:**
```python
/trading/accounts         # Trading accounts
/trading/orders          # Order management
/trading/portfolio       # Portfolio management
/trading/market-data     # Market information
```

## Service Modules (Alphabetical)

### 14. Analytics Module (`services/analytics/`)

**Purpose**: Business intelligence and analytics

**Key Components:**
- Transaction analytics and reporting
- User behavior tracking
- Financial reporting and insights
- Performance metrics and KPIs

**Status**: Migrated to services container

### 15. API Module (`services/api/`)

**Purpose**: External API integrations and third-party services

**Key Components:**
- Payment processor integration
- Credit bureau API connections
- Banking network APIs
- Fraud detection services

**Status**: Migrated to services container

### 16. Communications Module (`services/communications/`)

**Purpose**: Multi-channel communication services

**Key Components:**
- Email template management and sending
- SMS notifications and alerts
- Push notifications for mobile
- Communication preferences and delivery tracking

**Status**: Migrated to services container

### 17. Integrations Module (`services/integrations/`)

**Purpose**: Comprehensive third-party service integrations

**Key Components:**
- Payment gateway integrations (PayPal, Stripe, Flutterwave)
- Financial data providers (Plaid)
- Communication services (SendGrid, Twilio)
- Blockchain integrations (Binance, Polygonscan, NVCT Network)

**Sub-modules:**
- `communications/` - Communication integrations
  - `sendgrid/` - SendGrid email service
  - `twilio/` - Twilio SMS service
- `financial_data/` - Financial data providers
  - `plaid/` - Plaid banking data
- `payment_gateways/` - Payment processing
  - `paypal/` - PayPal integration
  - `stripe/` - Stripe payments
  - `flutterwave/` - Flutterwave payments
- `blockchain/` - Blockchain services
  - `binance/` - Binance integration
  - `analytics/` - Blockchain analytics

**Key Routes:**
```python
/integrations/                    # Integration overview
/integrations/communications      # Communication services
/integrations/financial-data      # Financial data providers
/integrations/payment-gateways    # Payment gateways
/integrations/blockchain          # Blockchain services
```

**Active Integrations:**
- Binance API for market data
- Polygonscan for blockchain exploration
- NVCT Network for stablecoin operations
- Plaid for banking data
- Multiple payment gateways

### 18. MFA Module (`services/mfa/`)

**Purpose**: Multi-factor authentication services

**Key Components:**
- SMS-based authentication
- Email verification codes
- Authenticator app integration
- Backup authentication codes

**Status**: Migrated to services container

### 19. Public Module (`public/`)

**Purpose**: Public-facing website and information

**Key Components:**
- Public website pages and documentation
- Contact forms and inquiries
- API documentation and health monitoring
- Marketing information and user guides

**Models:**
- `ContactInquiry` - Contact form submissions
- `PublicContent` - Public page content
- `FAQ` - Frequently asked questions

**Key Routes:**
```python
/                        # Homepage
/about                   # About page
/contact                 # Contact form
/services               # Services overview
/privacy-policy         # Privacy policy
/terms-of-service       # Terms of service
/documentation          # Documentation center
/api-documentation      # API documentation
/getting-started        # Getting started guide
/user-guide            # User guide
/faq                   # FAQ section
/nvct-whitepaper       # NVCT whitepaper
```

**API Endpoints:**
```python
POST /contact/submit           # Contact form submission
GET  /api/contact             # Contact API
GET  /api/health              # Health check
GET  /api/v1/public/services  # Available services
GET  /api/v1/public/news      # Latest news
GET  /api/v1/public/live-market-data  # Live market data
```

## Specialized Modules (Alphabetical)

### 20. NVCT Stablecoin Module (`nvct_stablecoin/`)

**Purpose**: NVCT stablecoin operations and management

**Key Components:**
- Stablecoin issuance and redemption
- Blockchain integration and wallet management
- Cross-chain operations
- Compliance and regulatory reporting

**Models:**
- `NVCTToken` - NVCT token management
- `StablecoinTransaction` - Token transactions
- `Wallet` - Digital wallet management
- `BlockchainIntegration` - Blockchain connections

**Status**: Active specialized module

### 21. Security Center Module (`security_center/`)

**Purpose**: Comprehensive security monitoring and management

**Key Components:**
- Real-time security event monitoring
- Advanced threat detection and response
- Vulnerability assessment and management
- Access control and authentication
- Data security implementation across all modules

**Models:**
- `SecurityEvent` - Security events and alerts
- `ThreatDetection` - Threat analysis and detection
- `AccessLog` - Comprehensive access logging
- `SecurityIncident` - Incident tracking and response
- `SecureUserProfile` - Encrypted user data

**Key Routes:**
```python
/security/events              # Security events monitoring
/security/threats             # Threat detection
/security/incidents           # Incident management
/security/access-logs         # Access logs
/security/vulnerability       # Vulnerability assessment
/security/vulnerability/export-data  # Export vulnerability data
```

**Security Features:**
- Data encryption for all protected modules
- Enhanced route security with input sanitization
- CSRF protection and rate limiting
- Comprehensive audit logging
- Multi-factor authentication enforcement

### 22. Sovereign Banking Module (`sovereign/`)

**Purpose**: Government and institutional banking services

**Key Components:**
- Government account management
- Institutional services and large transactions
- Specialized compliance and regulatory reporting
- High-value transaction processing

**Models:**
- `SovereignAccount` - Government accounts
- `InstitutionalService` - Institutional services
- `LargeTransaction` - High-value transactions
- `GovernmentCompliance` - Government compliance

**Status**: Active specialized module

### 23. Treasury Module (`treasury/`)

**Purpose**: Treasury operations and asset management

**Key Components:**
- Asset portfolio management
- Interest rate management and optimization
- Investment tracking and analysis
- Risk assessment and management
- Liquidity management and yield optimization

**Models:**
- `Asset` - Treasury assets and securities
- `Portfolio` - Asset portfolios with performance tracking
- `InterestRate` - Interest rate configurations
- `Investment` - Investment tracking and performance
- `RiskAssessment` - Risk evaluation and scoring

**Key Routes:**
```python
/treasury/assets         # Asset management
/treasury/portfolios     # Portfolio management
/treasury/rates         # Interest rate management
/treasury/investments   # Investment tracking
```

**Features:**
- Real-time asset valuation
- Risk-adjusted return calculations
- Automated rebalancing
- Regulatory compliance reporting

### 24. User Management Module (`user_management/`)

**Purpose**: Advanced user management for administrators

**Key Components:**
- Extended user profile management
- Role and permission management
- User analytics and reporting
- Bulk user operations and lifecycle management

**Models:**
- `UserProfile` - Extended user profiles
- `UserPreferences` - User preferences and settings
- `UserRole` - Role management and assignments
- `UserActivity` - Activity tracking and analytics

**Key Routes:**
```python
/user-management/users      # User management interface
/user-management/roles      # Role management
/user-management/analytics  # User analytics
/user-management/bulk       # Bulk operations
```

## Utility Modules (Alphabetical)

### 25. Utils Module (`utils/`)

**Purpose**: Shared utilities and helper functions

**Key Components:**
- Navigation service utilities
- Common helper functions and decorators
- Shared business logic
- Data processing helpers

**Key Files:**
- `services.py` - Navigation and utility services
- `helpers.py` - Common helper functions
- `decorators.py` - Utility decorators

## Module Registration and Management

### Active Module Registration

Based on `modular_blueprint_registration.py`, the following modules are actively registered:

**Core Operational Modules:**
- `public` - Public interface
- `auth` - Authentication
- `dashboard` - User dashboard
- `banking` - Core banking operations

**Tier 1 Banking Modules:**
- `accounts` - Account management
- `treasury` - Treasury operations
- `compliance` - Regulatory compliance
- `nvct_stablecoin` - Stablecoin operations
- `sovereign` - Sovereign banking

**Administrative Modules:**
- `admin_management` - System administration
- `security_center` - Security monitoring
- `user_management` - User management

**Service Container Modules:**
- `services/integrations` - Third-party integrations
- `services/communications` - Communication services
- `services/mfa` - Multi-factor authentication
- `services/api` - API services
- `services/analytics` - Analytics services

### Module Dependencies and Security

All modules implement:
- Role-based access control (RBAC)
- Comprehensive security measures
- Audit logging and monitoring
- Data encryption for sensitive information
- CSRF protection and rate limiting

### Module Health Monitoring

Each module includes:
- Health check endpoints
- Performance monitoring
- Error tracking and logging
- Security event monitoring
- Compliance validation

This modular architecture ensures scalability, maintainability, and clear separation of concerns across the entire NVC Banking Platform. Each module is designed to be self-contained while integrating seamlessly with the overall platform architecture.

---

**Related Documentation:**
- [Developer Guide](../development/DEVELOPER_GUIDE.md) - Complete development documentation
- [UI Development Guide](../DEVELOPER_GUIDE_UNIFIED_UI.md) - Template system and components
- [Security Implementation](../security/SECURITY_IMPLEMENTATION_STATUS.md) - Security framework
- [Operations Runbook](../operations/OPERATIONS_RUNBOOK.md) - Operational procedures

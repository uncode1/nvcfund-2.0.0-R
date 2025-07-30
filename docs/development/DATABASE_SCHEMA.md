# NVC Banking Platform - Database Schema & Relationships

## Database Overview

**Database**: PostgreSQL
**Schema Name**: nvcfund_db
**Total Tables**: 50+ tables across 31+ banking modules

## Core Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            NVC Banking Platform                                 │
│                           Database Relationships                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    USERS     │    │   ACCOUNTS   │    │ TRANSACTIONS │    │    CARDS     │
│              │    │              │    │              │    │              │
│ id (PK) INT  │◄──►│ user_id (FK) │◄──►│ account_id   │    │ account_id   │
│ username     │    │ account_num  │    │ amount       │    │ card_number  │
│ email        │    │ balance      │    │ timestamp    │    │ card_type    │
│ password_hash│    │ account_type │    │ description  │    │ status       │
│ created_at   │    │ status       │    │ status       │    │ expiry_date  │
│ role         │    │ created_at   │    │ created_at   │    │ created_at   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       │                    │                    │                    │
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ USER_PROFILE │    │   LOANS      │    │   PAYMENTS   │    │ CARD_LIMITS  │
│              │    │              │    │              │    │              │
│ user_id (FK) │    │ account_id   │    │ transaction_ │    │ card_id (FK) │
│ first_name   │    │ loan_amount  │    │ payment_type │    │ daily_limit  │
│ last_name    │    │ interest_rate│    │ merchant     │    │ monthly_limit│
│ phone        │    │ term_months  │    │ gateway      │    │ atm_limit    │
│ address      │    │ status       │    │ status       │    │ created_at   │
│ updated_at   │    │ created_at   │    │ created_at   │    └──────────────┘
└──────────────┘    └──────────────┘    └──────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│KYC_VERIFICATION│  │ INVESTMENTS  │    │   TREASURY   │
│              │    │              │    │              │
│ user_id (FK) │    │ account_id   │    │ position_id  │
│ document_type│    │ investment_  │    │ asset_type   │
│ status       │    │ amount       │    │ amount       │
│ verified_by  │    │ current_value│    │ maturity_date│
│ verified_at  │    │ return_rate  │    │ yield_rate   │
│ created_at   │    │ created_at   │    │ created_at   │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Security & Compliance Tables

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ AUDIT_LOGS   │    │   SESSIONS   │    │ MFA_TOKENS   │
│              │    │              │    │              │
│ id (PK)      │    │ session_id   │    │ user_id (FK) │
│ user_id (FK) │    │ user_id (FK) │    │ token_type   │
│ action       │    │ ip_address   │    │ secret_key   │
│ description  │    │ user_agent   │    │ is_active    │
│ ip_address   │    │ created_at   │    │ created_at   │
│ timestamp    │    │ last_activity│    │ expires_at   │
│ severity     │    │ is_active    │    └──────────────┘
└──────────────┘    └──────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌──────────────┐    ┌──────────────┐
│COMPLIANCE_   │    │ SECURITY_    │
│ACTIONS       │    │ EVENTS       │
│              │    │              │
│ id (PK)      │    │ id (PK)      │
│ user_id (FK) │    │ event_type   │
│ action_type  │    │ severity     │
│ status       │    │ description  │
│ assigned_to  │    │ ip_address   │
│ due_date     │    │ user_agent   │
│ created_at   │    │ timestamp    │
└──────────────┘    └──────────────┘
```

## Trading & Investment Tables

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│TRADING_      │    │ PORTFOLIOS   │    │   ORDERS     │
│ACCOUNTS      │    │              │    │              │
│              │    │ user_id (FK) │    │ portfolio_id │
│ user_id (FK) │    │ portfolio_   │    │ symbol       │
│ account_type │    │ total_value  │    │ order_type   │
│ balance      │    │ cash_balance │    │ quantity     │
│ margin_limit │    │ profit_loss  │    │ price        │
│ created_at   │    │ created_at   │    │ status       │
└──────────────┘    └──────────────┘    └──────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ POSITIONS    │    │   HOLDINGS   │    │ MARKET_DATA  │
│              │    │              │    │              │
│ portfolio_id │    │ portfolio_id │    │ symbol       │
│ symbol       │    │ symbol       │    │ price        │
│ quantity     │    │ quantity     │    │ volume       │
│ avg_price    │    │ market_value │    │ timestamp    │
│ market_value │    │ cost_basis   │    │ source       │
│ created_at   │    │ created_at   │    │ created_at   │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Islamic Banking & Stablecoin Tables

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ SUKUK_BONDS  │    │ NVCT_TOKENS  │    │ SMART_       │
│              │    │              │    │ CONTRACTS    │
│ id (PK)      │    │ id (PK)      │    │              │
│ sukuk_name   │    │ wallet_addr  │    │ contract_addr│
│ face_value   │    │ balance      │    │ contract_type│
│ profit_rate  │    │ last_tx_hash │    │ status       │
│ maturity_date│    │ created_at   │    │ deployed_at  │
│ sharia_status│    │ updated_at   │    │ gas_used     │
│ created_at   │    └──────────────┘    │ created_at   │
└──────────────┘                        └──────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ ZAKAT_       │    │ STABLECOIN_  │    │ BLOCKCHAIN_  │
│ CALCULATIONS │    │ RESERVES     │    │ ANALYTICS    │
│              │    │              │    │              │
│ user_id (FK) │    │ reserve_type │    │ network      │
│ wealth_amount│    │ amount       │    │ block_number │
│ zakat_due    │    │ backing_ratio│    │ tx_count     │
│ status       │    │ last_audit   │    │ volume       │
│ due_date     │    │ created_at   │    │ timestamp    │
│ created_at   │    └──────────────┘    └──────────────┘
└──────────────┘
```

## Key Relationships Summary

### Primary Relationships:
1. **Users → Accounts** (1:Many) - One user can have multiple accounts
2. **Accounts → Transactions** (1:Many) - Each account has multiple transactions
3. **Accounts → Cards** (1:Many) - Each account can have multiple cards
4. **Users → KYC Verification** (1:1) - Each user has one KYC record
5. **Users → Portfolios** (1:Many) - Users can have multiple investment portfolios

### Security Relationships:
1. **Users → Audit Logs** (1:Many) - All user actions are logged
2. **Users → Sessions** (1:Many) - Users can have multiple active sessions
3. **Users → MFA Tokens** (1:Many) - Multiple MFA tokens per user

### Financial Relationships:
1. **Portfolios → Holdings** (1:Many) - Each portfolio contains multiple holdings
2. **Accounts → Loans** (1:Many) - Accounts can have multiple loans
3. **Transactions → Payments** (1:1) - Each transaction may have payment details

## Data Types & Constraints

### Common Field Types:
- **Primary Keys**: INTEGER (auto-increment)
- **Foreign Keys**: INTEGER (references parent table)
- **Monetary Amounts**: DECIMAL(15,2) - Supports up to $999,999,999,999.99
- **Timestamps**: TIMESTAMP WITH TIME ZONE
- **Status Fields**: VARCHAR(20) with CHECK constraints
- **UUIDs**: VARCHAR(36) for session IDs and correlation IDs

### Security Constraints:
- All sensitive fields encrypted at rest using AES-256
- Foreign key constraints enforced for data integrity
- Check constraints for valid status values
- Unique constraints on email, username, account numbers
- Index optimization for frequently queried fields

## Performance Optimization

### Indexes:
- Primary key indexes on all tables
- Composite indexes on (user_id, created_at) for timeline queries
- Partial indexes on active records only
- Full-text search indexes on description fields

### Partitioning:
- Transaction tables partitioned by month
- Audit logs partitioned by quarter
- Archive policies for data older than 7 years

This schema supports the full NVC Banking Platform with enterprise-grade security, compliance, and scalability requirements.
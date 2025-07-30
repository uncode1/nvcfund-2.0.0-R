# NVC Banking Platform - API Documentation

## Overview

The NVC Banking Platform provides a comprehensive RESTful API for banking operations, user management, and financial services. This documentation covers all available endpoints, authentication methods, and usage examples.

## Base URL

```
Production: https://api.nvcfund.com/v1
Development: http://localhost:5000/api
```

## Authentication

### API Key Authentication
```http
Authorization: Bearer YOUR_API_KEY
```

### Session Authentication
```http
Cookie: session=SESSION_TOKEN
X-CSRFToken: CSRF_TOKEN
```

### JWT Authentication
```http
Authorization: Bearer JWT_TOKEN
```

## Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request is invalid",
    "details": {}
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

## Authentication Endpoints

### POST /api/auth/login
Authenticate user and create session.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 123,
      "username": "user@example.com",
      "role": "standard_user",
      "first_name": "John",
      "last_name": "Doe"
    },
    "token": "jwt_token_here",
    "expires_at": "2024-01-01T18:00:00Z"
  }
}
```

**Error Codes:**
- `INVALID_CREDENTIALS` - Invalid username or password
- `ACCOUNT_LOCKED` - Account is temporarily locked
- `ACCOUNT_INACTIVE` - Account is deactivated

### POST /api/auth/logout
Logout user and invalidate session.

**Response:**
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

### GET /api/auth/profile
Get current user profile information.

**Headers:**
```http
Authorization: Bearer JWT_TOKEN
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "standard_user",
    "account_type": "individual",
    "is_verified": true,
    "created_at": "2024-01-01T12:00:00Z",
    "last_login": "2024-01-01T15:30:00Z"
  }
}
```

### PUT /api/auth/profile
Update user profile information.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "Anytown",
  "state": "CA",
  "zip_code": "12345"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  },
  "message": "Profile updated successfully"
}
```

## Banking Endpoints

### GET /api/banking/accounts
Get user's bank accounts.

**Query Parameters:**
- `type` (optional) - Filter by account type (checking, savings, business)
- `status` (optional) - Filter by status (active, inactive, closed)
- `limit` (optional) - Number of results (default: 50, max: 100)
- `offset` (optional) - Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "data": {
    "accounts": [
      {
        "id": 456,
        "account_number": "****7890",
        "account_type": "checking",
        "account_name": "Primary Checking",
        "current_balance": "1250.75",
        "available_balance": "1200.75",
        "currency": "USD",
        "status": "active",
        "opening_date": "2024-01-01T12:00:00Z"
      }
    ],
    "total_count": 1,
    "has_more": false
  }
}
```

### POST /api/banking/accounts
Create new bank account.

**Request Body:**
```json
{
  "account_type": "savings",
  "account_name": "Emergency Savings",
  "initial_deposit": "500.00",
  "currency": "USD"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 789,
    "account_number": "****1234",
    "account_type": "savings",
    "account_name": "Emergency Savings",
    "current_balance": "500.00",
    "status": "active"
  },
  "message": "Account created successfully"
}
```

### GET /api/banking/accounts/{account_id}/transactions
Get account transactions.

**Path Parameters:**
- `account_id` - Account ID

**Query Parameters:**
- `start_date` (optional) - Start date (YYYY-MM-DD)
- `end_date` (optional) - End date (YYYY-MM-DD)
- `type` (optional) - Transaction type (credit, debit, transfer)
- `limit` (optional) - Number of results (default: 50, max: 100)
- `offset` (optional) - Pagination offset

**Response:**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": 12345,
        "amount": "100.00",
        "transaction_type": "debit",
        "description": "ATM Withdrawal",
        "status": "completed",
        "created_at": "2024-01-01T14:30:00Z",
        "merchant_name": "ATM Location",
        "reference_number": "TXN123456"
      }
    ],
    "total_count": 1,
    "has_more": false
  }
}
```

### POST /api/banking/transfers
Create money transfer.

**Request Body:**
```json
{
  "from_account_id": 456,
  "to_account_id": 789,
  "amount": "250.00",
  "description": "Transfer to savings",
  "transfer_type": "internal"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transaction_id": 67890,
    "reference_number": "TXN789012",
    "status": "pending",
    "estimated_completion": "2024-01-01T16:00:00Z"
  },
  "message": "Transfer initiated successfully"
}
```

## Card Management Endpoints

### GET /api/banking/cards
Get user's cards.

**Response:**
```json
{
  "success": true,
  "data": {
    "cards": [
      {
        "id": 111,
        "card_number": "****1234",
        "card_type": "debit",
        "card_holder_name": "John Doe",
        "expiry_date": "2025-12-31",
        "status": "active",
        "daily_limit": "1000.00",
        "account_id": 456
      }
    ]
  }
}
```

### POST /api/banking/cards/{card_id}/block
Block a card.

**Path Parameters:**
- `card_id` - Card ID

**Request Body:**
```json
{
  "reason": "Lost card"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Card blocked successfully"
}
```

### POST /api/banking/cards/{card_id}/unblock
Unblock a card.

**Response:**
```json
{
  "success": true,
  "message": "Card unblocked successfully"
}
```

## Dashboard Endpoints

### GET /api/dashboard/summary
Get dashboard summary data.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_balance": "2750.75",
    "available_balance": "2700.75",
    "pending_transactions": 2,
    "recent_transactions": [
      {
        "id": 12345,
        "amount": "100.00",
        "description": "ATM Withdrawal",
        "created_at": "2024-01-01T14:30:00Z"
      }
    ],
    "account_summary": [
      {
        "account_type": "checking",
        "balance": "1250.75",
        "account_count": 1
      },
      {
        "account_type": "savings",
        "balance": "1500.00",
        "account_count": 1
      }
    ]
  }
}
```

## Error Codes

### Authentication Errors
- `INVALID_CREDENTIALS` - Invalid username or password
- `ACCOUNT_LOCKED` - Account is temporarily locked
- `ACCOUNT_INACTIVE` - Account is deactivated
- `TOKEN_EXPIRED` - JWT token has expired
- `TOKEN_INVALID` - JWT token is invalid
- `INSUFFICIENT_PERMISSIONS` - User lacks required permissions

### Banking Errors
- `ACCOUNT_NOT_FOUND` - Account does not exist
- `INSUFFICIENT_FUNDS` - Not enough funds for transaction
- `DAILY_LIMIT_EXCEEDED` - Transaction exceeds daily limit
- `ACCOUNT_FROZEN` - Account is frozen
- `INVALID_AMOUNT` - Invalid transaction amount
- `TRANSFER_FAILED` - Transfer could not be processed

### General Errors
- `INVALID_REQUEST` - Request format is invalid
- `MISSING_PARAMETER` - Required parameter is missing
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `SERVER_ERROR` - Internal server error
- `SERVICE_UNAVAILABLE` - Service temporarily unavailable

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Standard Users**: 1000 requests per hour
- **Premium Users**: 5000 requests per hour
- **Admin Users**: 10000 requests per hour

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination using `limit` and `offset` parameters:

```http
GET /api/banking/transactions?limit=25&offset=50
```

Response includes pagination metadata:
```json
{
  "data": {
    "items": [...],
    "total_count": 150,
    "limit": 25,
    "offset": 50,
    "has_more": true
  }
}
```

## Webhooks

The API supports webhooks for real-time notifications:

### Webhook Events
- `transaction.created` - New transaction created
- `transaction.completed` - Transaction completed
- `account.created` - New account created
- `card.blocked` - Card was blocked
- `user.login` - User logged in

### Webhook Payload
```json
{
  "event": "transaction.created",
  "data": {
    "transaction_id": 12345,
    "account_id": 456,
    "amount": "100.00",
    "type": "debit"
  },
  "timestamp": "2024-01-01T14:30:00Z",
  "webhook_id": "wh_123456789"
}
```

## SDKs and Libraries

Official SDKs are available for:
- **JavaScript/Node.js**: `npm install nvc-banking-sdk`
- **Python**: `pip install nvc-banking-sdk`
- **PHP**: `composer require nvc/banking-sdk`
- **Java**: Maven/Gradle dependency available

## Testing

### Sandbox Environment
Use the sandbox environment for testing:
```
Base URL: https://sandbox-api.nvcfund.com/v1
```

### Test Credentials
```
Username: test@example.com
Password: testpassword123
API Key: test_sk_123456789
```

### Test Cards
```
Debit Card: 4111111111111111
Credit Card: 5555555555554444
Expired Card: 4000000000000002
```

## Support

For API support:
- **Documentation**: https://docs.nvcfund.com/api
- **Support Email**: api-support@nvcfund.com
- **Developer Portal**: https://developers.nvcfund.com
- **Status Page**: https://status.nvcfund.com

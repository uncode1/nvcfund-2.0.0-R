# NVC Banking Platform - Developer Onboarding Guide

Welcome to the NVC Banking Platform development team! This guide will help you get up and running quickly with our codebase.

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://python.org/downloads/)
- **PostgreSQL 14+** - [Download PostgreSQL](https://postgresql.org/download/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)
- **VS Code** (recommended) - [Download VS Code](https://code.visualstudio.com/)

### 1. Clone the Repository

```bash
git clone https://github.com/nvcfund/nvcfund-2.0.0.git
cd nvcfund-2.0.0
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r nvcfund-backend/requirements.txt
```

### 3. Set Up Database

```bash
# Create PostgreSQL database
createdb nvc_banking_dev

# Set environment variables
export DATABASE_URL="postgresql://username:password@localhost/nvc_banking_dev"
export SECRET_KEY="your-secret-key-here"
export DEBUG="true"
```

### 4. Initialize Database

```bash
cd nvcfund-backend
python -c "from app_factory import create_app; from modules.core.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 5. Run the Application

```bash
# Development server
python main.py

# Or using the development script
python start_dev.py
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
nvcfund-2.0.0/
├── nvcfund-backend/           # Backend Flask application
│   ├── modules/               # Modular application components
│   │   ├── auth/             # Authentication module
│   │   ├── banking/          # Banking operations
│   │   ├── treasury/         # Treasury management
│   │   ├── compliance/       # Compliance features
│   │   ├── dashboard/        # Dashboard module
│   │   └── core/             # Core utilities and extensions
│   ├── scripts/              # Utility scripts
│   └── config.py             # Application configuration
├── nvcfund-frontend/         # (Separate) Frontend application
├── tests/                    # Test suite
├── docs/                     # Documentation
└── scripts/                  # Project scripts
```

## 🏗️ Architecture Overview

### Modular Architecture

The NVC Banking Platform uses a **pure modular architecture** where each feature is self-contained:

```python
# Each module contains:
modules/banking/
├── __init__.py              # Module initialization
├── routes.py                # Flask routes
├── models.py                # Database models
├── services.py              # Business logic
├── forms.py                 # WTForms for data validation

### Key Components

1. **Flask Application Factory** (`app_factory.py`)
   - Creates and configures the Flask app
   - Registers all modules
   - Sets up extensions and middleware

2. **Core Extensions** (`modules/core/extensions.py`)
   - Database (SQLAlchemy)
   - Authentication (Flask-Login)
   - Security (CSRF, Rate Limiting)
   - Caching and Sessions

3. **Security Framework** (`modules/security_center/`)
   - Data encryption
   - Access control
   - Audit logging
   - Threat detection

4. **Database Models** (Each module's `models.py`)
   - SQLAlchemy ORM models
   - Relationships and constraints
   - Business logic methods

## 🔧 Development Workflow

### 1. Creating a New Feature

```bash
# Create feature branch
git checkout -b feature/new-feature-name

# Make your changes
# ... code changes ...

# Run tests
python run_tests.py --unit

# Commit changes
git add .
git commit -m "feat: add new feature description"

# Push and create PR
git push origin feature/new-feature-name
```

### 2. Adding a New Module

```bash
# Create module directory
mkdir nvcfund-backend/modules/new_module

# Create module files
touch nvcfund-backend/modules/new_module/__init__.py
touch nvcfund-backend/modules/new_module/routes.py
touch nvcfund-backend/modules/new_module/models.py
touch nvcfund-backend/modules/new_module/services.py
```

**Module Template:**

```python
# __init__.py
from flask import Blueprint

new_module_bp = Blueprint('new_module', __name__, url_prefix='/new-module')

from . import routes

# routes.py
from flask import jsonify
from flask_login import login_required
from . import new_module_bp

@new_module_bp.route('/')
@login_required
def index():
    return jsonify({'message': 'Welcome to the new module API!'})

# models.py
from modules.core.extensions import db
from datetime import datetime

class NewModel(db.Model):
    __tablename__ = 'new_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 3. Database Migrations

```bash
# Create migration
python -c "from modules.core.database_migration import create_migration; create_migration('add_new_table')"

# Apply migrations
python -c "from modules.core.database_migration import apply_migrations; apply_migrations()"
```

### 4. Testing

```bash
# Run all tests
python run_tests.py --all

# Run specific test types
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --performance

# Run specific test file
python run_tests.py --test tests/unit/test_auth_models.py

# Run with coverage
python run_tests.py --coverage
```

## 🎨 Frontend Development

### Headless Backend & React Frontend

The NVC Banking Platform operates with a **headless architecture**. The Flask backend serves as a pure JSON API, and it does not render any HTML templates.

The frontend is a separate, modern **React Single-Page Application (SPA)**. All UI components, pages, and interactions are handled by the React codebase.

**Key Points for Developers:**
- **API-Driven**: All features are exposed through RESTful API endpoints. Your work on the backend will primarily involve creating and maintaining these endpoints.
- **JSON Communication**: The backend communicates with the frontend exclusively through JSON.
- **Decoupled Workflow**: Backend and frontend development can occur in parallel. Refer to the API documentation for endpoint contracts.
- **No Template Engine**: You will not be working with Jinja2 or any other server-side template engine.

## 🔒 Security Guidelines

### 1. Authentication & Authorization

```python
from modules.core.security_decorators import require_permission
from modules.core.rbac import require_role

@require_permission('banking_access')
def banking_operation():
    # Your code here
    pass

@require_role('admin')
def admin_operation():
    # Your code here
    pass
```

### 2. Data Encryption

```python
from modules.security_center.secure_models import BankingAccountSecureMixin

class BankAccount(BankingAccountSecureMixin, db.Model):
    # Automatically encrypts sensitive fields
    pass

# Usage
account.set_account_number('1234567890')  # Encrypted storage
masked = account.get_masked_account_number()  # Returns ****7890
```

### 3. Input Validation

```python
from modules.core.input_validation import validate_input

@validate_input(
    amount='amount',
    account_number='account_number',
    email='email'
)
def transfer_funds(amount, account_number, email):
    # Inputs are automatically validated
    pass
```

## 📊 Database Guidelines

### 1. Model Conventions

```python
class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'  # Use snake_case
    __table_args__ = {'extend_existing': True}  # Allow model updates
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Required fields
    account_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Optional fields with defaults
    status = db.Column(db.String(20), default='active')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. Relationships

```python
# One-to-Many
class User(db.Model):
    accounts = db.relationship('BankAccount', backref='owner', lazy='dynamic')

class BankAccount(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
```

### 3. Query Optimization

```python
# ✅ Use eager loading for relationships
accounts = BankAccount.query.options(
    db.joinedload(BankAccount.owner)
).all()

# ✅ Use pagination for large datasets
accounts = BankAccount.query.paginate(
    page=1, per_page=50, error_out=False
)

# ✅ Use indexes for frequently queried fields
account_number = db.Column(db.String(20), index=True)
```

## 🧪 Testing Guidelines

### 1. Unit Tests

```python
import pytest
from modules.auth.models import User

class TestUserModel:
    def test_user_creation(self, db_session):
        user = User(username='test', email='test@example.com')
        user.set_password('password123')
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.check_password('password123')
```

### 2. Integration Tests

```python
class TestAuthenticationAPI:
    def test_login_success(self, client, test_user):
        response = client.post('/api/auth/login', json={
            'username': test_user.username,
            'password': 'testpassword123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
```

### 3. Performance Tests

```python
@pytest.mark.performance
def test_query_performance(self, db_session, performance_timer):
    performance_timer.start()
    users = User.query.all()
    performance_timer.stop()
    
    assert performance_timer.elapsed < 1.0  # Should be under 1 second
```

## 🚀 Deployment

### Development Deployment

```bash
# Run development server
python main.py

# Run with debug mode
DEBUG=true python main.py
```

### Production Deployment

```bash
# Use Gunicorn
gunicorn --config gunicorn.conf.py main:app

# Or use the production script
python nvcfund-backend/scripts/production_startup.py
```

## 📚 Resources

### Documentation
- [API Documentation](../api/API_DOCUMENTATION.md)
- [Security Guide](../security/DATA_SECURITY_GUIDE.md)
- [Database Schema](DATABASE_SCHEMA.md)
- [UI Design System](../UI_DESIGN_SYSTEM.md)

### Tools & Extensions
- **VS Code Extensions:**
  - Python
  - Flask Snippets
  - SQLAlchemy
  - Jinja2
  - GitLens

### Useful Commands

```bash
# Code quality checks
python nvcfund-backend/scripts/code_quality_analyzer.py

# Database operations
python -c "from app_factory import create_app; from modules.core.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"

# Run specific module tests
python run_tests.py --test tests/unit/test_banking_models.py

# Generate coverage report
python run_tests.py --coverage
```

## 🆘 Getting Help

- **Slack**: #nvc-development
- **Email**: dev-team@nvcfund.com
- **Documentation**: https://docs.nvcfund.com
- **Issue Tracker**: GitHub Issues

## 📝 Contributing

1. Follow the [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) branching model
2. Write tests for new features
3. Update documentation
4. Follow code style guidelines
5. Submit pull requests for review

Welcome to the team! 🎉

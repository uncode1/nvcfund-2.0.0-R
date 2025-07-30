"""
Core Constants for NVC Banking Platform
Centralized configuration constants for API health status and other system-wide values
"""

class APIHealthStatus:
    """API Health Status Constants"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OPERATIONAL = "operational"

class APIResponse:
    """Standard API Response Constants"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ModuleStatus:
    """Module Registration and Status Constants"""
    REGISTERED = "registered"
    FAILED = "failed"
    SKIPPED = "skipped"
    CONFLICT = "conflict"

class SecurityEvents:
    """Security Event Type Constants"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    AUTHENTICATION_REQUIRED = "authentication_required"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class BankingOperations:
    """Banking Operation Type Constants"""
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    EXCHANGE = "exchange"
    SETTLEMENT = "settlement"

# Default Configuration Values
DEFAULT_API_VERSION = "1.0.0"
DEFAULT_MODULE_VERSION = "1.0.0"
DEFAULT_RATE_LIMIT = 60  # requests per minute
DEFAULT_SESSION_TIMEOUT = 900  # 15 minutes in seconds

# Banking Industry Standards
PCI_DSS_COMPLIANCE = True
FFIEC_COMPLIANCE = True
SOX_COMPLIANCE = True
GDPR_COMPLIANCE = True
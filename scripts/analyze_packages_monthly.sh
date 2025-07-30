#!/bin/bash
# Monthly Package Analysis Script for NVC Banking Platform
# READ-ONLY analysis - generates recommendations for CI/CD pipeline deployment
# NEVER modifies packages directly

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
BACKUP_DIR="$PROJECT_ROOT/backups"
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Ensure directories exist
mkdir -p "$LOG_DIR" "$BACKUP_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/monthly_update_$DATE.log"
}

# Error handler
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Cleanup function
cleanup() {
    if [ -d "$TEMP_ENV" ]; then
        rm -rf "$TEMP_ENV"
    fi
}

# Set trap for cleanup
trap cleanup EXIT

log "Starting monthly package analysis for CI/CD deployment planning (READ-ONLY)"

# Change to project directory
cd "$PROJECT_ROOT"

# 1. Create comprehensive backup
log "Creating comprehensive backup..."
BACKUP_FILE="$BACKUP_DIR/complete_backup_$TIMESTAMP.tar.gz"
pip freeze > "$BACKUP_DIR/requirements_backup_$TIMESTAMP.txt"
tar -czf "$BACKUP_FILE" \
    --exclude='logs/*' \
    --exclude='backups/*' \
    --exclude='__pycache__/*' \
    --exclude='*.pyc' \
    --exclude='venv*' \
    --exclude='node_modules' \
    . || error_exit "Failed to create backup"

log "Backup created: $BACKUP_FILE"

# 2. Run pre-update security validation
log "Running pre-update security validation..."
python3 scripts/check_security.py > "$LOG_DIR/pre_update_security_$TIMESTAMP.txt" 2>&1
PRE_UPDATE_EXIT_CODE=$?

# 3. Document current environment (READ-ONLY)
log "Documenting current environment state..."
pip freeze > "$LOG_DIR/current_environment_$TIMESTAMP.txt"
log "Current environment documented for CI/CD reference"

# 4. Identify packages to update
log "Identifying packages for update..."
PACKAGES_TO_UPDATE=$(pip list --outdated --format=json)
echo "$PACKAGES_TO_UPDATE" > "$LOG_DIR/packages_to_update_$TIMESTAMP.json"

# Extract critical packages
CRITICAL_PACKAGES=(
    "flask"
    "sqlalchemy"
    "flask-login"
    "flask-jwt-extended"
    "cryptography"
    "werkzeug"
    "gunicorn"
)

HIGH_PRIORITY_PACKAGES=(
    "flask-cors"
    "flask-limiter"
    "flask-socketio"
    "flask-sqlalchemy"
    "flask-session"
    "flask-wtf"
    "psycopg2-binary"
)

BANKING_PACKAGES=(
    "plaid-python"
    "pyjwt"
    "pyotp"
    "qrcode"
    "reportlab"
    "weasyprint"
    "web3"
)

# 5. Analyze packages by category (READ-ONLY)
analyze_package_category() {
    local category_name="$1"
    shift
    local packages=("$@")
    
    log "Analyzing $category_name packages (read-only)..."
    
    local analysis_file="$LOG_DIR/analysis_${category_name}_$TIMESTAMP.txt"
    
    for package in "${packages[@]}"; do
        if echo "$PACKAGES_TO_UPDATE" | jq -r '.[].name' | grep -qi "^$package$"; then
            current_version=$(pip show "$package" | grep Version | cut -d' ' -f2)
            latest_version=$(echo "$PACKAGES_TO_UPDATE" | jq -r ".[] | select(.name | ascii_downcase == \"$package\") | .latest_version")
            
            log "Analysis: $package: $current_version -> $latest_version"
            echo "$package: $current_version -> $latest_version" >> "$analysis_file"
            echo "  Priority: $category_name" >> "$analysis_file"
            echo "  Recommendation: Update through CI/CD pipeline" >> "$analysis_file"
            echo "" >> "$analysis_file"
        fi
    done
}

# Analyze critical packages (read-only)
analyze_package_category "critical" "${CRITICAL_PACKAGES[@]}"

# Analyze high priority packages (read-only)
analyze_package_category "high_priority" "${HIGH_PRIORITY_PACKAGES[@]}"

# Analyze banking-specific packages (read-only)
analyze_package_category "banking" "${BANKING_PACKAGES[@]}"

# 6. Run current environment validation (READ-ONLY)
log "Running current environment validation..."
TEST_RESULTS_FILE="$LOG_DIR/test_results_$TIMESTAMP.txt"

# Test Flask application startup
log "Testing Flask application startup..."
python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/nvcfund-backend')
from app_factory import create_app
app = create_app('testing')
print('Flask application startup: OK')
" >> "$TEST_RESULTS_FILE" 2>&1 || {
    log "ERROR: Flask application startup test failed"
    echo "Flask application startup: FAILED" >> "$TEST_RESULTS_FILE"
}

# Test database connectivity
log "Testing database connectivity..."
python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/nvcfund-backend')
from app_factory import create_app
app = create_app('testing')
with app.app_context():
    from modules.core.extensions import db
    result = db.engine.execute('SELECT 1').scalar()
    assert result == 1
    print('Database connectivity: OK')
" >> "$TEST_RESULTS_FILE" 2>&1 || {
    log "ERROR: Database connectivity test failed"
    echo "Database connectivity: FAILED" >> "$TEST_RESULTS_FILE"
}

# Test authentication system
log "Testing authentication system..."
python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/nvcfund-backend')
from modules.auth.services import AuthService
print('Authentication system: OK')
" >> "$TEST_RESULTS_FILE" 2>&1 || {
    log "ERROR: Authentication system test failed"
    echo "Authentication system: FAILED" >> "$TEST_RESULTS_FILE"
}

# Test banking modules
log "Testing banking modules..."
python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/nvcfund-backend')
from modules.banking.services import BankingService
print('Banking modules: OK')
" >> "$TEST_RESULTS_FILE" 2>&1 || {
    log "ERROR: Banking modules test failed"
    echo "Banking modules: FAILED" >> "$TEST_RESULTS_FILE"
}

# Run pytest if available
if command -v pytest >/dev/null 2>&1; then
    log "Running pytest suite..."
    pytest "tests/" -v --tb=short >> "$TEST_RESULTS_FILE" 2>&1 || {
        log "WARNING: Some pytest tests failed"
    }
fi

# 7. Check for dependency conflicts
log "Checking for dependency conflicts..."
pip check > "$LOG_DIR/dependency_check_$TIMESTAMP.txt" 2>&1 || {
    log "WARNING: Dependency conflicts detected"
}

# 8. Document analysis results (READ-ONLY)
log "Documenting analysis results..."
echo "Analysis completed at $(date)" > "$LOG_DIR/analysis_summary_$TIMESTAMP.txt"
echo "No package modifications made - analysis only" >> "$LOG_DIR/analysis_summary_$TIMESTAMP.txt"

# 9. Environment validation complete
log "Environment validation completed - no modifications made"

# 10. Evaluate test results
log "Evaluating test results..."
if grep -q "FAILED" "$TEST_RESULTS_FILE"; then
    log "ERROR: Critical tests failed - update aborted"
    echo "Update Status: FAILED" > "$LOG_DIR/update_status_$TIMESTAMP.txt"
    exit 1
else
    log "All tests passed - update ready for deployment"
    echo "Update Status: READY" > "$LOG_DIR/update_status_$TIMESTAMP.txt"
fi

# 11. Final security validation (READ-ONLY)
log "Running final security validation..."
python3 scripts/check_security.py > "$LOG_DIR/final_security_validation_$TIMESTAMP.txt" 2>&1
FINAL_VALIDATION_EXIT_CODE=$?

# 12. Security validation summary  
log "Security validation summary..."
if [ $FINAL_VALIDATION_EXIT_CODE -eq 0 ]; then
    log "Current environment security validation passed"
    echo "Security Status: CURRENT_ENVIRONMENT_OK" >> "$LOG_DIR/analysis_status_$TIMESTAMP.txt"
else
    log "Current environment has security concerns"
    echo "Security Status: REQUIRES_ATTENTION" >> "$LOG_DIR/analysis_status_$TIMESTAMP.txt"
fi

# 13. Generate comprehensive update report
REPORT_FILE="$LOG_DIR/monthly_update_report_$TIMESTAMP.txt"
{
    echo "NVC Banking Platform - Monthly Update Report"
    echo "==========================================="
    echo "Date: $(date)"
    echo "Update Status: $(grep 'Update Status:' "$LOG_DIR/update_status_$TIMESTAMP.txt" | cut -d' ' -f3)"
    echo "Security Status: $(grep 'Security Status:' "$LOG_DIR/analysis_status_$TIMESTAMP.txt" | cut -d' ' -f3)"
    echo ""
    echo "Packages Updated:"
    echo "=================="
    
    # Compare before and after requirements
    if [ -f "$BACKUP_DIR/requirements_backup_$TIMESTAMP.txt" ] && [ -f "$LOG_DIR/updated_requirements_$TIMESTAMP.txt" ]; then
        diff "$BACKUP_DIR/requirements_backup_$TIMESTAMP.txt" "$LOG_DIR/updated_requirements_$TIMESTAMP.txt" | grep "^>" | sed 's/^> /Updated: /' || echo "No package changes detected"
    fi
    
    echo ""
    echo "Test Results Summary:"
    echo "===================="
    cat "$TEST_RESULTS_FILE"
    
    echo ""
    echo "Dependency Check:"
    echo "=================="
    if [ -f "$LOG_DIR/dependency_check_$TIMESTAMP.txt" ]; then
        cat "$LOG_DIR/dependency_check_$TIMESTAMP.txt"
    else
        echo "No dependency issues detected"
    fi
    
    echo ""
    echo "Next Steps:"
    echo "==========="
    echo "⚠️  ANALYSIS ONLY - NO DIRECT UPDATES PERFORMED"
    echo "1. Review this analysis report thoroughly"
    echo "2. Create CI/CD branch for package updates"
    echo "3. Test updates in isolated development environment"
    echo "4. Deploy through CI/CD pipeline to staging"
    echo "5. Deploy to production through proper pipeline"
    echo "6. Monitor application performance post-deployment"
    
    echo ""
    echo "CI/CD Deployment Instructions:"
    echo "============================="
    echo "For CI/CD pipeline deployment:"
    echo "1. Use analysis files as input for CI/CD updates"
    echo "2. Test package updates in development branch"
    echo "3. Deploy through staging environment first"
    echo "4. Use blue-green deployment for production"
    echo "5. Monitor and rollback through CI/CD if needed"
    
} > "$REPORT_FILE"

# 14. Generate CI/CD deployment documentation
if grep -q "READY" "$LOG_DIR/update_status_$TIMESTAMP.txt"; then
    CICD_DOC="$PROJECT_ROOT/cicd_deployment_plan_$TIMESTAMP.md"
    {
        echo "# CI/CD Deployment Plan - $TIMESTAMP"
        echo "## Analysis Summary"
        echo "Monthly package analysis completed successfully."
        echo ""
        echo "## Deployment Strategy"
        echo "⚠️  Use CI/CD pipeline - DO NOT execute updates directly"
        echo ""
        echo "### Step 1: Create Feature Branch"
        echo "\`\`\`bash"
        echo "git checkout -b feature/package-updates-$TIMESTAMP"
        echo "\`\`\`"
        echo ""
        echo "### Step 2: Update Requirements in Development"
        echo "Review analysis files and update requirements.txt in development environment"
        echo ""
        echo "### Step 3: CI/CD Pipeline Deployment"
        echo "Push branch and let CI/CD handle testing and deployment"
        echo ""
        echo "### Analysis Files Generated:"
        echo "- Current environment: $LOG_DIR/current_environment_$TIMESTAMP.txt"
        echo "- Package analysis: $LOG_DIR/packages_to_update_$TIMESTAMP.json"
        echo "- Security validation: $LOG_DIR/final_security_validation_$TIMESTAMP.txt"
        echo ""
        echo "⚠️  NEVER run pip install --upgrade on live production"
    } > "$CICD_DOC"
    
    log "CI/CD deployment plan created: $CICD_DOC"
fi

# 15. Send notification
log "Sending update notification..."
UPDATE_STATUS=$(grep 'Update Status:' "$LOG_DIR/update_status_$TIMESTAMP.txt" | cut -d' ' -f3)

if [ "$UPDATE_STATUS" = "READY" ]; then
    NOTIFICATION_MESSAGE="✅ Monthly package updates completed successfully for NVC Banking Platform. Ready for deployment."
elif [ "$UPDATE_STATUS" = "FAILED" ]; then
    NOTIFICATION_MESSAGE="❌ Monthly package updates failed for NVC Banking Platform. Manual intervention required."
else
    NOTIFICATION_MESSAGE="⚠️ Monthly package updates completed with warnings for NVC Banking Platform. Review required."
fi

# Send notification (if webhook configured)
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"$NOTIFICATION_MESSAGE\"}" \
        "$SLACK_WEBHOOK_URL" || {
        log "Warning: Failed to send Slack notification"
    }
fi

log "Monthly update process completed"
log "Update report: $REPORT_FILE"
log "Update status: $UPDATE_STATUS"

# Return appropriate exit code
if [ "$UPDATE_STATUS" = "READY" ]; then
    exit 0
else
    exit 1
fi
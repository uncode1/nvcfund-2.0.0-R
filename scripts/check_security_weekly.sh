#!/bin/bash
# Weekly Security Check for NVC Banking Platform
# Automated security vulnerability scanning and critical update detection

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
REPORT_DIR="$LOG_DIR/security_reports"
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Ensure directories exist
mkdir -p "$LOG_DIR" "$REPORT_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/weekly_security_$DATE.log"
}

log "Starting weekly security check for NVC Banking Platform"

# Change to project directory
cd "$PROJECT_ROOT"

# 1. Run security validation
log "Running security validation..."
python3 scripts/check_security.py > "$REPORT_DIR/security_validation_$TIMESTAMP.txt" 2>&1
SECURITY_EXIT_CODE=$?

# 2. Check for critical Flask updates
log "Checking for critical Flask ecosystem updates..."
pip list --outdated --format=json | jq -r '.[] | select(.name | ascii_downcase | contains("flask")) | "\(.name): \(.version) -> \(.latest_version)"' > "$REPORT_DIR/flask_updates_$TIMESTAMP.txt"

# 3. Check for high-priority banking libraries
log "Checking banking-specific library updates..."
BANKING_PACKAGES=("plaid-python" "pyjwt" "pyotp" "cryptography" "sqlalchemy" "werkzeug" "gunicorn")
for package in "${BANKING_PACKAGES[@]}"; do
    pip list --outdated --format=json | jq -r ".[] | select(.name == \"$package\") | \"\(.name): \(.version) -> \(.latest_version)\"" >> "$REPORT_DIR/banking_updates_$TIMESTAMP.txt"
done

# 4. Generate security vulnerability report (READ-ONLY)
log "Generating vulnerability report (read-only scan)..."
pip-audit --format=json --output="$REPORT_DIR/vulnerabilities_$TIMESTAMP.json" 2>/dev/null || {
    log "Warning: pip-audit failed, documenting current package versions"
    # Safe fallback - only document current state
    pip list --format=json > "$REPORT_DIR/package_versions_$TIMESTAMP.json"
}

# 5. Check for dependency conflicts using pip check
log "Checking for dependency conflicts..."
pip check > "$REPORT_DIR/dependency_check_$TIMESTAMP.txt" 2>&1 || {
    log "Dependency conflicts detected - manual review required"
}

# 6. Analyze critical updates
CRITICAL_UPDATES=0
if [ -s "$REPORT_DIR/flask_updates_$TIMESTAMP.txt" ]; then
    CRITICAL_UPDATES=$((CRITICAL_UPDATES + $(wc -l < "$REPORT_DIR/flask_updates_$TIMESTAMP.txt")))
fi

if [ -s "$REPORT_DIR/banking_updates_$TIMESTAMP.txt" ]; then
    CRITICAL_UPDATES=$((CRITICAL_UPDATES + $(wc -l < "$REPORT_DIR/banking_updates_$TIMESTAMP.txt")))
fi

# 7. Generate summary report
SUMMARY_FILE="$REPORT_DIR/weekly_summary_$TIMESTAMP.txt"
{
    echo "NVC Banking Platform - Weekly Security Summary"
    echo "=============================================="
    echo "Date: $(date)"
    echo "Security Scan Exit Code: $SECURITY_EXIT_CODE"
    echo "Critical Updates Available: $CRITICAL_UPDATES"
    echo ""
    echo "Flask Updates:"
    if [ -s "$REPORT_DIR/flask_updates_$TIMESTAMP.txt" ]; then
        cat "$REPORT_DIR/flask_updates_$TIMESTAMP.txt"
    else
        echo "No Flask updates available"
    fi
    echo ""
    echo "Banking Library Updates:"
    if [ -s "$REPORT_DIR/banking_updates_$TIMESTAMP.txt" ]; then
        cat "$REPORT_DIR/banking_updates_$TIMESTAMP.txt"
    else
        echo "No banking library updates available"
    fi
    echo ""
    echo "Security Vulnerabilities:"
    if [ -f "$REPORT_DIR/vulnerabilities_$TIMESTAMP.json" ]; then
        echo "Vulnerability report generated: vulnerabilities_$TIMESTAMP.json"
        # Extract vulnerability count
        VULN_COUNT=$(jq -r '.vulnerabilities | length' "$REPORT_DIR/vulnerabilities_$TIMESTAMP.json" 2>/dev/null || echo "0")
        echo "Total vulnerabilities found: $VULN_COUNT"
    else
        echo "No vulnerability report available"
    fi
} > "$SUMMARY_FILE"

# 8. Alert conditions
ALERT_NEEDED=false
ALERT_MESSAGE=""

if [ $SECURITY_EXIT_CODE -ne 0 ]; then
    ALERT_NEEDED=true
    ALERT_MESSAGE="CRITICAL: Security vulnerabilities detected in NVC Banking Platform"
fi

if [ $CRITICAL_UPDATES -gt 0 ]; then
    ALERT_NEEDED=true
    ALERT_MESSAGE="$ALERT_MESSAGE\nCritical Flask/Banking updates available: $CRITICAL_UPDATES packages"
fi

# 9. Send alerts if needed
if [ "$ALERT_NEEDED" = true ]; then
    log "ALERT: Critical security issues detected"
    
    # Email alert (if configured)
    if command -v mail >/dev/null 2>&1; then
        {
            echo "Subject: NVC Banking Platform Security Alert"
            echo "From: security@nvcfund.com"
            echo "To: admin@nvcfund.com"
            echo ""
            echo -e "$ALERT_MESSAGE"
            echo ""
            echo "Full report available at: $SUMMARY_FILE"
        } | mail -s "NVC Banking Platform Security Alert" admin@nvcfund.com || {
            log "Warning: Failed to send email alert"
        }
    fi
    
    # Slack webhook (if configured)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 NVC Banking Platform Security Alert\n$ALERT_MESSAGE\"}" \
            "$SLACK_WEBHOOK_URL" || {
            log "Warning: Failed to send Slack alert"
        }
    fi
    
    # Discord webhook (if configured)
    if [ -n "$DISCORD_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"content\":\"🚨 **NVC Banking Platform Security Alert**\n$ALERT_MESSAGE\"}" \
            "$DISCORD_WEBHOOK_URL" || {
            log "Warning: Failed to send Discord alert"
        }
    fi
fi

# 10. Cleanup old reports (keep last 30 days)
log "Cleaning up old security reports..."
find "$REPORT_DIR" -name "*.txt" -o -name "*.json" | xargs ls -t | tail -n +100 | xargs -r rm

# 11. Create maintenance recommendations
MAINTENANCE_FILE="$REPORT_DIR/maintenance_recommendations_$TIMESTAMP.txt"
{
    echo "NVC Banking Platform - Maintenance Recommendations"
    echo "================================================"
    echo "Generated: $(date)"
    echo ""
    
    if [ $CRITICAL_UPDATES -gt 0 ]; then
        echo "IMMEDIATE ACTIONS REQUIRED:"
        echo "- Review and test critical package updates"
        echo "- Create backup before applying updates"
        echo "- Follow staged deployment process"
        echo ""
    fi
    
    if [ $SECURITY_EXIT_CODE -ne 0 ]; then
        echo "SECURITY ACTIONS REQUIRED:"
        echo "- Review vulnerability report: vulnerabilities_$TIMESTAMP.json"
        echo "- Apply security patches within 24 hours"
        echo "- Verify application functionality after updates"
        echo ""
    fi
    
    echo "ROUTINE MAINTENANCE:"
    echo "- Monthly comprehensive package review scheduled"
    echo "- Quarterly dependency audit recommended"
    echo "- Annual security assessment due"
    echo ""
    
    echo "NEXT STEPS:"
    echo "1. Review this report and summary"
    echo "2. Create update branch in version control"
    echo "3. Test updates in isolated development environment"
    echo "4. Run CI/CD pipeline with security validation"
    echo "5. Deploy through staging → production pipeline"
    echo "6. Monitor application post-deployment"
    echo ""
    echo "⚠️  NEVER apply updates directly to live production"
    
} > "$MAINTENANCE_FILE"

log "Weekly security check completed"
log "Summary report: $SUMMARY_FILE"
log "Maintenance recommendations: $MAINTENANCE_FILE"

# Return appropriate exit code
if [ $SECURITY_EXIT_CODE -ne 0 ] || [ $CRITICAL_UPDATES -gt 0 ]; then
    log "Security attention required - exiting with code 1"
    exit 1
else
    log "No critical security issues detected"
    exit 0
fi
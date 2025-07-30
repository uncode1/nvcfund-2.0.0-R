#!/bin/bash
# Setup Cron Jobs for NVC Banking Platform Package Management
# Automated scheduling for security checks and package updates

set -e

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Setting up cron jobs for NVC Banking Platform package management"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    log "This script should be run with sudo privileges for system-wide cron jobs"
    log "Running as current user for user-specific cron jobs..."
    USER_CRON=true
else
    USER_CRON=false
fi

# Create cron job entries
CRON_ENTRIES="# NVC Banking Platform - Automated Package Management
# Weekly security check every Monday at 2 AM
0 2 * * 1 cd $PROJECT_ROOT && ./scripts/weekly_security_check.sh >> $PROJECT_ROOT/logs/cron_security.log 2>&1

# Monthly package update on first Sunday of each month at 3 AM
0 3 1-7 * 0 cd $PROJECT_ROOT && ./scripts/monthly_package_update.sh >> $PROJECT_ROOT/logs/cron_monthly.log 2>&1

# Daily pip-audit security scan at 6 AM
0 6 * * * cd $PROJECT_ROOT && pip-audit --format=json --output=$PROJECT_ROOT/logs/daily_audit_\$(date +\%Y\%m\%d).json >> $PROJECT_ROOT/logs/cron_daily.log 2>&1

# Weekly log cleanup on Saturday at 11 PM
0 23 * * 6 find $PROJECT_ROOT/logs -name '*.log' -mtime +30 -delete && find $PROJECT_ROOT/logs -name '*.json' -mtime +30 -delete
"

# Backup existing crontab
log "Backing up existing crontab..."
if crontab -l > /dev/null 2>&1; then
    crontab -l > "$PROJECT_ROOT/backups/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
    log "Crontab backup created in backups directory"
else
    log "No existing crontab found"
fi

# Add new cron jobs
log "Adding NVC Banking Platform cron jobs..."

# Create temporary cron file
TEMP_CRON=$(mktemp)

# Get existing cron jobs (if any)
if crontab -l > /dev/null 2>&1; then
    crontab -l > "$TEMP_CRON"
fi

# Check if our cron jobs already exist
if grep -q "NVC Banking Platform" "$TEMP_CRON" 2>/dev/null; then
    log "NVC Banking Platform cron jobs already exist, updating..."
    # Remove existing NVC Banking Platform entries
    sed -i '/# NVC Banking Platform/,/^$/d' "$TEMP_CRON"
fi

# Add new cron jobs
echo "$CRON_ENTRIES" >> "$TEMP_CRON"

# Install the new crontab
crontab "$TEMP_CRON"

# Clean up temporary file
rm "$TEMP_CRON"

log "Cron jobs installed successfully"

# Display installed cron jobs
log "Current cron jobs:"
crontab -l | grep -A 10 -B 1 "NVC Banking Platform"

# Create systemd service files for more robust scheduling (optional)
if systemctl --version > /dev/null 2>&1 && [ "$USER_CRON" = false ]; then
    log "Creating systemd service files for enhanced scheduling..."
    
    # Weekly security check service
    cat > /etc/systemd/system/nvcfund-security-check.service << EOF
[Unit]
Description=NVC Banking Platform Weekly Security Check
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=$PROJECT_ROOT
ExecStart=$PROJECT_ROOT/scripts/weekly_security_check.sh
StandardOutput=append:$PROJECT_ROOT/logs/systemd_security.log
StandardError=append:$PROJECT_ROOT/logs/systemd_security.log

[Install]
WantedBy=multi-user.target
EOF

    # Weekly security check timer
    cat > /etc/systemd/system/nvcfund-security-check.timer << EOF
[Unit]
Description=Run NVC Banking Platform Security Check Weekly
Requires=nvcfund-security-check.service

[Timer]
OnCalendar=Mon *-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

    # Monthly update service
    cat > /etc/systemd/system/nvcfund-monthly-update.service << EOF
[Unit]
Description=NVC Banking Platform Monthly Update
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=$PROJECT_ROOT
ExecStart=$PROJECT_ROOT/scripts/monthly_package_update.sh
StandardOutput=append:$PROJECT_ROOT/logs/systemd_monthly.log
StandardError=append:$PROJECT_ROOT/logs/systemd_monthly.log

[Install]
WantedBy=multi-user.target
EOF

    # Monthly update timer
    cat > /etc/systemd/system/nvcfund-monthly-update.timer << EOF
[Unit]
Description=Run NVC Banking Platform Monthly Update
Requires=nvcfund-monthly-update.service

[Timer]
OnCalendar=Sun *-*-01..07 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

    # Reload systemd and enable timers
    systemctl daemon-reload
    systemctl enable nvcfund-security-check.timer
    systemctl enable nvcfund-monthly-update.timer
    systemctl start nvcfund-security-check.timer
    systemctl start nvcfund-monthly-update.timer
    
    log "Systemd services and timers created and enabled"
    
    # Display timer status
    systemctl list-timers nvcfund-*
fi

# Create monitoring script for cron job health
cat > "$PROJECT_ROOT/scripts/monitor_cron_health.sh" << 'EOF'
#!/bin/bash
# Monitor health of NVC Banking Platform cron jobs

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
DATE=$(date +%Y%m%d)

# Check if security check ran today
if [ ! -f "$LOG_DIR/cron_security.log" ] || ! grep -q "$(date +%Y-%m-%d)" "$LOG_DIR/cron_security.log"; then
    echo "WARNING: Security check may not have run today"
fi

# Check if monthly update ran this month (if it's past the 7th)
if [ $(date +%d) -gt 7 ]; then
    if [ ! -f "$LOG_DIR/cron_monthly.log" ] || ! grep -q "$(date +%Y-%m)" "$LOG_DIR/cron_monthly.log"; then
        echo "WARNING: Monthly update may not have run this month"
    fi
fi

# Check if daily audit is running
if [ ! -f "$LOG_DIR/daily_audit_$DATE.json" ]; then
    echo "WARNING: Daily audit may not have run today"
fi

# Check log file sizes (detect if they're growing abnormally)
for log_file in "$LOG_DIR"/*.log; do
    if [ -f "$log_file" ]; then
        size=$(wc -c < "$log_file")
        if [ $size -gt 10485760 ]; then  # 10MB
            echo "WARNING: Log file $log_file is larger than 10MB"
        fi
    fi
done

echo "Cron job health check completed"
EOF

chmod +x "$PROJECT_ROOT/scripts/monitor_cron_health.sh"

# Create email notification setup script
cat > "$PROJECT_ROOT/scripts/setup_email_notifications.sh" << 'EOF'
#!/bin/bash
# Setup email notifications for NVC Banking Platform security alerts

# Configuration
ADMIN_EMAIL="admin@nvcfund.com"
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"

echo "Setting up email notifications for security alerts..."

# Check if mail command is available
if ! command -v mail >/dev/null 2>&1; then
    echo "Installing mail utilities..."
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y mailutils
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y mailx
    else
        echo "Please install mail utilities manually"
        exit 1
    fi
fi

# Configure postfix/sendmail for basic email functionality
echo "Configuring mail system..."
echo "Please ensure your system is configured to send emails"
echo "For Gmail SMTP, you may need to:"
echo "1. Create an app password in your Google Account"
echo "2. Configure /etc/postfix/main.cf with SMTP relay settings"
echo "3. Set up proper authentication"

# Test email functionality
echo "Testing email functionality..."
echo "This is a test email from NVC Banking Platform security monitoring" | mail -s "Test Email - NVC Banking Platform" "$ADMIN_EMAIL" && {
    echo "Test email sent successfully"
} || {
    echo "Failed to send test email - please check configuration"
}

echo "Email notification setup completed"
EOF

chmod +x "$PROJECT_ROOT/scripts/setup_email_notifications.sh"

# Create webhook notification setup script
cat > "$PROJECT_ROOT/scripts/setup_webhook_notifications.sh" << 'EOF'
#!/bin/bash
# Setup webhook notifications for NVC Banking Platform

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Setting up webhook notifications for NVC Banking Platform..."

# Create environment file for webhook URLs
ENV_FILE="$PROJECT_ROOT/.env.notifications"

if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'ENVEOF'
# Webhook URLs for NVC Banking Platform notifications
# Uncomment and configure the webhooks you want to use

# Slack webhook URL
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Discord webhook URL
# DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK

# Microsoft Teams webhook URL
# TEAMS_WEBHOOK_URL=https://yourorg.webhook.office.com/webhookb2/YOUR/TEAMS/WEBHOOK

# Custom webhook URL
# CUSTOM_WEBHOOK_URL=https://your-custom-endpoint.com/webhook
ENVEOF

    echo "Environment file created: $ENV_FILE"
    echo "Please edit this file to configure your webhook URLs"
else
    echo "Environment file already exists: $ENV_FILE"
fi

# Test webhook functionality
echo "Testing webhook functionality..."
source "$ENV_FILE"

if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"🧪 Test notification from NVC Banking Platform security monitoring"}' \
        "$SLACK_WEBHOOK_URL" && {
        echo "Slack webhook test successful"
    } || {
        echo "Slack webhook test failed"
    }
fi

if [ -n "$DISCORD_WEBHOOK_URL" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data '{"content":"🧪 Test notification from NVC Banking Platform security monitoring"}' \
        "$DISCORD_WEBHOOK_URL" && {
        echo "Discord webhook test successful"
    } || {
        echo "Discord webhook test failed"
    }
fi

echo "Webhook notification setup completed"
EOF

chmod +x "$PROJECT_ROOT/scripts/setup_webhook_notifications.sh"

# Ensure log directory exists
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/backups"

# Set proper permissions
chmod +x "$PROJECT_ROOT/scripts"/*.sh

log "Cron job setup completed successfully!"
log ""
log "What was set up:"
log "- Weekly security checks (Mondays at 2 AM)"
log "- Monthly package updates (First Sunday of month at 3 AM)"
log "- Daily security audits (Daily at 6 AM)"
log "- Weekly log cleanup (Saturdays at 11 PM)"
log "- Systemd timers (if available)"
log "- Health monitoring script"
log "- Email notification setup script"
log "- Webhook notification setup script"
log ""
log "Next steps:"
log "1. Run ./scripts/setup_email_notifications.sh to configure email alerts"
log "2. Run ./scripts/setup_webhook_notifications.sh to configure webhook alerts"
log "3. Test the setup with: ./scripts/monitor_cron_health.sh"
log "4. Monitor logs in $PROJECT_ROOT/logs/"
log ""
log "Manual testing:"
log "- Test weekly security check: ./scripts/weekly_security_check.sh"
log "- Test monthly update: ./scripts/monthly_package_update.sh"
log "- Test security monitor: python3 scripts/security_monitor.py"
# NVC Banking Platform - Troubleshooting Manual

## Overview

This manual provides comprehensive troubleshooting procedures for the NVC Banking Platform, covering development debugging, production diagnostics, and performance optimization.

## Environment-Based Logging

### Development Mode Logging

In development, detailed transfer channel logging is automatically enabled to help debug routing issues:

```bash
# Enable development mode
export FLASK_ENV=development

# Or enable transfer debugging specifically
export DEBUG_TRANSFERS=true
```

**Development logs show:**
- Channel parameter resolution: `🎯 CHANNEL RESOLUTION: swift-transfer -> swift_transfer`
- Template serving details: `🎯 SERVING: Template=wire_transfer.html, Channel=swift_transfer, Title=SWIFT Transfer`
- Response details: `🎯 RESPONSE DETAILS: 200 OK | Served: Template=wire_transfer.html, Channel=swift_transfer, Title=SWIFT Transfer | URL: /banking/transfers/new?channel=swift_transfer`

### Production Mode Logging

In production, logging is minimal by default to avoid performance impact:

```bash
# Production environment (default)
unset FLASK_ENV
unset DEBUG_TRANSFERS
```

**Production logs show:**
- Minimal channel resolution: `Transfer channel served: swift_transfer -> banking/transfers/wire_transfer.html`

### Verbose Troubleshooting in Production

When troubleshooting issues in production, enable verbose transfer logging temporarily:

```bash
# Enable verbose transfer logging for troubleshooting
export DEBUG_TRANSFERS=true

# Restart the application to apply changes
sudo systemctl restart nvc-banking-platform

# After troubleshooting, disable verbose logging
unset DEBUG_TRANSFERS
sudo systemctl restart nvc-banking-platform
```

## Transfer Channel Debugging

### Common Transfer Routing Issues

1. **Channel Parameter Mismatch**
   - **Symptom**: Transfer redirects to internal transfer instead of intended channel
   - **Cause**: Frontend sends hyphen format (`swift-transfer`) but backend expects underscore (`swift_transfer`)
   - **Debug**: Enable `DEBUG_TRANSFERS=true` to see channel resolution mapping

2. **Missing Channel Configuration**
   - **Symptom**: Transfer defaults to internal transfer
   - **Cause**: Channel not defined in `channel_configs` dictionary
   - **Debug**: Check logs for "Channel not found in configurations" messages

3. **Template Not Found**
   - **Symptom**: 500 error when accessing transfer page
   - **Cause**: Template file missing or incorrect path
   - **Debug**: Check `X-Template-Used` header in response

### Response Headers for Debugging

The platform includes troubleshooting headers in development mode:

```http
X-Served-Channel: swift_transfer
X-Template-Used: banking/transfers/wire_transfer.html
X-Final-URL: /banking/transfers/new?channel=swift_transfer
```

Use browser developer tools to inspect these headers when debugging routing issues.

## Data Integrity and System Stability

To prevent data loss or corruption, the platform is built with several safeguards.

### 1. Atomic Database Transactions

All database operations within a single API request are handled within a transaction. This ensures that a series of related changes either all succeed or all fail together, preventing partially updated or inconsistent data.

### 2. Automatic Rollback on Error

If an unhandled error occurs during a request (resulting in a 500-level error), the system automatically performs a **database rollback**. This cancels any database changes made during that failed request, ensuring the database remains in a clean, consistent state. This is a critical safeguard against data corruption from unexpected failures.

### 3. Database Migrations

Schema changes are managed through a migration system. This ensures that database structure changes are applied consistently and safely, preserving existing data.

## Log Categories and Locations

### Application Logs
- **Location**: `/var/log/nvc-banking/`
- **Main Log**: `application.log`
- **Error Log**: `error.log`
- **Transfer Log**: `transfers.log`

### Security Logs
- **Location**: `/var/log/nvc-banking/security/`
- **Categories**: authentication, authorization, audit, compliance, etc.

### Database Logs
- **PostgreSQL**: `/var/log/postgresql/`
- **Connection Pool**: Check application logs for connection issues

## Performance Monitoring

### Key Metrics to Monitor

1. **Response Times**
   - Target: < 200ms for standard pages
   - Target: < 500ms for complex transfers

2. **Error Rates**
   - Target: < 0.1% for critical operations
   - Monitor 4xx and 5xx responses

3. **Transfer Success Rates**
   - Target: > 99.5% for all transfer channels
   - Monitor failed transfer attempts

### Monitoring Commands

```bash
# Real-time log monitoring
tail -f /var/log/nvc-banking/application.log

# Transfer-specific monitoring
tail -f /var/log/nvc-banking/transfers.log | grep "🎯"

# Error monitoring
tail -f /var/log/nvc-banking/error.log

# Performance monitoring
grep "Response time" /var/log/nvc-banking/application.log | tail -20
```

## Common Issues and Solutions

### 1. Transfer Channel Routing Issues

**Problem**: SWIFT transfer shows internal transfer interface

**Solution**:
```bash
# Enable debug logging
export DEBUG_TRANSFERS=true

# Test the problematic transfer
curl -H "X-Debug: true" "https://your-domain.com/banking/transfers/new?channel=swift-transfer"

# Check logs for channel resolution
grep "CHANNEL RESOLUTION" /var/log/nvc-banking/transfers.log
```

### 2. High Response Times

**Problem**: Transfer pages loading slowly

**Investigation**:
```bash
# Check database connections
grep "database" /var/log/nvc-banking/application.log | tail -10

# Monitor memory usage
free -h
ps aux | grep gunicorn

# Check for deadlocks
grep "deadlock" /var/log/postgresql/postgresql-*.log
```

### 3. Authentication Issues

**Problem**: Users unable to access transfer pages

**Investigation**:
```bash
# Check authentication logs
grep "authentication" /var/log/nvc-banking/security/authentication.log

# Check session issues
grep "session" /var/log/nvc-banking/application.log | tail -20
```

## Emergency Procedures

### 1. Disable Verbose Logging in Production

If verbose logging was accidentally left enabled in production:

```bash
# Immediately disable
unset DEBUG_TRANSFERS
unset FLASK_ENV

# Restart application
sudo systemctl restart nvc-banking-platform

# Verify logging level
grep "🎯" /var/log/nvc-banking/application.log | wc -l
# Should return 0 in production
```

### 2. Transfer Service Degradation

If transfer services are experiencing issues:

```bash
# Check all transfer channels
for channel in swift wire ach paypal stripe; do
  echo "Testing $channel..."
  curl -s -o /dev/null -w "%{http_code}" "https://your-domain.com/banking/transfers/new?channel=${channel}-transfer"
done
```

### 3. Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection pool
grep "connection" /var/log/nvc-banking/application.log | tail -10

# Check active connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

## Log Rotation and Cleanup

### Automatic Log Rotation

Logs are automatically rotated using logrotate:

```bash
# Check logrotate configuration
cat /etc/logrotate.d/nvc-banking

# Force log rotation (if needed)
sudo logrotate -f /etc/logrotate.d/nvc-banking
```

### Manual Cleanup

```bash
# Clean old logs (older than 30 days)
find /var/log/nvc-banking/ -name "*.log.*" -mtime +30 -delete

# Compress large current logs
gzip /var/log/nvc-banking/application.log.1
```

## Contact and Escalation

### Support Levels

1. **Level 1**: Application logs and basic troubleshooting
2. **Level 2**: Database and performance issues
3. **Level 3**: Security incidents and data corruption

### Emergency Contacts

- **Technical Lead**: technical-lead@nvcfund.com
- **DevOps Team**: devops@nvcfund.com
- **Security Team**: security@nvcfund.com

---

**Last Updated**: July 8, 2025
**Version**: 1.0
**Maintainer**: NVC Banking Platform Team
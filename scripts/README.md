# NVC Banking Platform - Scripts Directory

## Overview
This directory contains production-safe scripts for package management and security monitoring that follow proper naming conventions without adjectives.

## Scripts

### Security Management
- **`check_security.py`** - Fast security validation for live applications (read-only)
- **`check_security_weekly.sh`** - Automated weekly security monitoring
- **`plan_updates.py`** - Generate CI/CD deployment plans (read-only analysis)

### Package Management
- **`analyze_packages_monthly.sh`** - Monthly package analysis for CI/CD planning
- **`setup_automation.sh`** - Configure cron jobs and automation

## Usage Guidelines

### Production Safety
- ✅ All scripts are 100% read-only - NO package modifications whatsoever
- ✅ NO pip install or pip upgrade commands in any script
- ✅ Scripts only analyze, document, and generate CI/CD deployment plans
- ✅ ALL package updates go through CI/CD pipelines exclusively

### Naming Conventions
- Scripts use action-based naming without adjectives
- Format: `{action}_{target}[_{frequency}].{extension}`
- Examples: `check_security.py`, `plan_updates.py`, `setup_automation.sh`

### Execution
```bash
# Security validation (safe on live apps)
python3 scripts/check_security.py

# Weekly security monitoring
./scripts/check_security_weekly.sh

# Generate update plans for CI/CD
python3 scripts/plan_updates.py

# Setup automation
sudo ./scripts/setup_automation.sh
```

All scripts follow banking-grade security practices and production-safe operations.
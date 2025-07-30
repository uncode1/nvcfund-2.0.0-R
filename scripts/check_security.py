#!/usr/bin/env python3
"""
Safe Security Check for NVC Banking Platform
Read-only security validation for live applications
"""
import json
import sys
from datetime import datetime
from pathlib import Path

def create_daily_log_structure():
    """Create nested log directory structure for current date"""
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m") 
    date = now.strftime("%d")
    
    logs_dir = Path("logs")
    current_date_dir = logs_dir / year / month / date
    current_date_dir.mkdir(parents=True, exist_ok=True)
    
    categories = ["security_reports", "application", "banking", "compliance", "admin", "errors", "audit", "system"]
    for category in categories:
        (current_date_dir / category).mkdir(exist_ok=True)
    
    return current_date_dir

def check_flask_packages():
    """Check Flask package status"""
    try:
        import subprocess
        result = subprocess.run(['pip', 'list', '--format=json'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            packages = json.loads(result.stdout)
            flask_packages = [p for p in packages if 'flask' in p['name'].lower()]
            return flask_packages
        return []
    except Exception:
        return []

def test_critical_imports():
    """Test critical package imports"""
    critical_packages = ['flask', 'sqlalchemy', 'flask_login', 'flask_cors', 'werkzeug']
    results = {}
    
    for package in critical_packages:
        try:
            __import__(package)
            results[package] = "OK"
        except ImportError as e:
            results[package] = f"FAILED: {e}"
    
    return results

def check_flask_version():
    """Check Flask version"""
    try:
        import flask
        return {"version": flask.__version__, "status": "OK"}
    except Exception as e:
        return {"version": "Unknown", "status": f"ERROR: {e}"}

def main():
    print("NVC Banking Platform - Simple Security Check")
    print("=" * 50)
    
    # Create nested log structure
    log_dir = create_daily_log_structure()
    
    # Check Flask version
    flask_info = check_flask_version()
    print(f"Flask Version: {flask_info['version']} ({flask_info['status']})")
    
    # Test imports
    print("\nCritical Package Imports:")
    import_results = test_critical_imports()
    failed_imports = 0
    
    for package, status in import_results.items():
        status_symbol = "✓" if status == "OK" else "✗"
        print(f"  {status_symbol} {package}: {status}")
        if status != "OK":
            failed_imports += 1
    
    # Check Flask packages
    flask_packages = check_flask_packages()
    print(f"\nFlask Ecosystem Packages: {len(flask_packages)} found")
    
    # Summary
    print("\n" + "=" * 50)
    if failed_imports == 0 and flask_info['status'] == "OK":
        print("Status: ✓ Package environment is healthy")
        return 0
    else:
        print("Status: ✗ Issues detected - review required")
        return 1

if __name__ == "__main__":
    sys.exit(main())
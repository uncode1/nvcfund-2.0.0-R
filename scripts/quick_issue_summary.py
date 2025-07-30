#!/usr/bin/env python3
"""
Quick Issue Summary from Link Testing
Identifies critical issues found during comprehensive testing
"""

import requests
from datetime import datetime

def test_critical_endpoints():
    """Test the specific endpoints that showed errors"""
    base_url = "http://localhost:5000"
    
    # Login as super admin first
    session = requests.Session()
    
    # Login
    login_data = {
        'username': 'uncode',
        'password': 'Zx9Wq2@#ComplexCeo'
    }
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    
    critical_endpoints = [
        ("/trading", "Trading Platform"),
        ("/admin", "Admin Dashboard"), 
        ("/compliance", "Compliance Dashboard"),
        ("/dashboard/main-dashboard", "Main Dashboard"),
        ("/banking", "Banking Operations"),
        ("/treasury", "Treasury Management")
    ]
    
    issues_found = []
    working_endpoints = []
    
    print("Critical Endpoint Testing")
    print("=" * 40)
    
    for endpoint, name in critical_endpoints:
        try:
            response = session.get(f"{base_url}{endpoint}", timeout=10)
            
            status = response.status_code
            final_url = response.url
            
            if status == 500:
                issues_found.append({
                    'endpoint': endpoint,
                    'name': name,
                    'issue': 'SERVER ERROR (500)',
                    'severity': 'CRITICAL'
                })
                print(f"❌ {name}: SERVER ERROR (500)")
                
            elif status == 403:
                issues_found.append({
                    'endpoint': endpoint,
                    'name': name,
                    'issue': 'FORBIDDEN (403)',
                    'severity': 'HIGH'
                })
                print(f"🔒 {name}: FORBIDDEN (403)")
                
            elif status in [200, 302]:
                working_endpoints.append({
                    'endpoint': endpoint,
                    'name': name,
                    'status': status
                })
                print(f"✅ {name}: OK ({status})")
                
            else:
                issues_found.append({
                    'endpoint': endpoint,
                    'name': name,
                    'issue': f'HTTP {status}',
                    'severity': 'MEDIUM'
                })
                print(f"⚠️ {name}: HTTP {status}")
                
        except Exception as e:
            issues_found.append({
                'endpoint': endpoint,
                'name': name,
                'issue': f'CONNECTION ERROR: {str(e)}',
                'severity': 'CRITICAL'
            })
            print(f"💥 {name}: CONNECTION ERROR")
    
    return {
        'issues_found': issues_found,
        'working_endpoints': working_endpoints,
        'total_tested': len(critical_endpoints),
        'issues_count': len(issues_found)
    }

def generate_quick_report(results):
    """Generate quick issue summary"""
    
    report = f"""# NVC Banking Platform - Critical Issues Summary

**Test Date**: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
**Authentication**: Super Admin Session
**Critical Endpoints Tested**: {results['total_tested']}
**Issues Found**: {results['issues_count']}

## Critical Issues Identified

"""
    
    for issue in results['issues_found']:
        severity_icon = {
            'CRITICAL': '🔴',
            'HIGH': '🟠', 
            'MEDIUM': '🟡'
        }.get(issue['severity'], '⚪')
        
        report += f"### {severity_icon} {issue['name']} - {issue['severity']}\n"
        report += f"- **Endpoint**: {issue['endpoint']}\n"
        report += f"- **Issue**: {issue['issue']}\n\n"
    
    if results['working_endpoints']:
        report += "## Working Endpoints ✅\n\n"
        for endpoint in results['working_endpoints']:
            report += f"- **{endpoint['name']}**: {endpoint['endpoint']} (HTTP {endpoint['status']})\n"
        report += "\n"
    
    report += """## Immediate Actions Required

1. **Fix Trading Module**: 500 server error needs immediate attention
2. **Resolve Admin Dashboard**: Template or routing issues
3. **Debug Compliance Module**: JavaScript dependency issues
4. **Verify Authentication**: Ensure proper role-based access

## From Server Logs Observed:

- **Trading Module**: Template rendering error (500)
- **Admin Dashboard**: JSON syntax error "unexpected '}'"
- **Compliance Dashboard**: JavaScript error "'moment' is undefined"
- **Dashboard Routing**: Endpoint naming issues

"""
    
    return report

if __name__ == "__main__":
    results = test_critical_endpoints()
    report = generate_quick_report(results)
    
    # Save report
    with open("docs/CRITICAL_ISSUES_SUMMARY.md", "w") as f:
        f.write(report)
    
    print("\n" + "=" * 40)
    print(f"Critical Issues Found: {results['issues_count']}")
    print(f"Working Endpoints: {len(results['working_endpoints'])}")
    print("Report saved: docs/CRITICAL_ISSUES_SUMMARY.md")
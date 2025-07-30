#!/usr/bin/env python3
"""
RBAC Security Testing Script
NVC Banking Platform - Role-Based Access Control Security Verification
Version: 3.0.0 - Security-First Testing
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set
import json

class RBACSecurityTester:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.security_issues = []
        self.security_passes = []
        
        # Define role hierarchy
        self.role_hierarchy = {
            'guest': 0,
            'user': 1,
            'treasury': 2,
            'compliance': 2,
            'manager': 3,
            'admin': 4
        }
        
        # Define critical permissions
        self.critical_permissions = [
            'can_access_admin',
            'can_view_finra_codes',
            'can_edit_transactions',
            'can_export_transactions',
            'can_access_treasury',
            'can_manage_users',
            'can_view_audit_logs'
        ]
    
    def run_security_tests(self) -> Dict:
        """Run all RBAC security tests"""
        print("🔐 Running RBAC Security Tests...")
        print("=" * 50)
        
        # Test template security
        self.test_template_security()
        
        # Test JavaScript security
        self.test_javascript_security()
        
        # Test CSS security (for role-based styling)
        self.test_css_security()
        
        # Generate security report
        return self.generate_security_report()
    
    def test_template_security(self):
        """Test templates for proper RBAC implementation"""
        print("🛡️  Testing Template Security...")
        
        template_files = list(self.base_path.rglob("*.html"))
        
        for template_file in template_files:
            if self.should_skip_file(template_file):
                continue
                
            try:
                content = template_file.read_text(encoding='utf-8')
                self.test_template_rbac(template_file, content)
            except Exception as e:
                self.add_security_issue(f"Failed to read template {template_file}: {e}")
        
        print(f"   ✅ Tested {len([f for f in template_files if not self.should_skip_file(f)])} templates")
    
    def test_template_rbac(self, file_path: Path, content: str):
        """Test individual template for RBAC security"""
        
        # Test 1: Check for unprotected sensitive operations
        self.test_unprotected_operations(file_path, content)
        
        # Test 2: Check for proper permission checks
        self.test_permission_checks(file_path, content)
        
        # Test 3: Check for role-based visibility
        self.test_role_visibility(file_path, content)
        
        # Test 4: Check for data exposure
        self.test_data_exposure(file_path, content)
        
        # Test 5: Check for CSRF protection
        self.test_csrf_protection(file_path, content)
    
    def test_unprotected_operations(self, file_path: Path, content: str):
        """Test for unprotected sensitive operations"""
        
        # Look for sensitive operations without permission checks
        sensitive_operations = [
            r'url_for\(["\'].*admin.*["\']',
            r'url_for\(["\'].*delete.*["\']',
            r'url_for\(["\'].*edit.*["\']',
            r'url_for\(["\'].*manage.*["\']',
            r'url_for\(["\'].*export.*["\']'
        ]
        
        for operation_pattern in sensitive_operations:
            matches = re.findall(operation_pattern, content, re.IGNORECASE)
            
            for match in matches:
                # Check if there's a permission check nearby
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if match in line:
                        # Check surrounding lines for permission checks
                        context_start = max(0, i - 5)
                        context_end = min(len(lines), i + 5)
                        context = '\n'.join(lines[context_start:context_end])
                        
                        if 'check_permission' not in context and 'if current_user' not in context:
                            self.add_security_issue(f"{file_path}: Potentially unprotected operation: {match}")
                        else:
                            self.add_security_pass(f"{file_path}: Protected operation: {match}")
    
    def test_permission_checks(self, file_path: Path, content: str):
        """Test for proper permission check implementation"""
        
        # Look for permission checks
        permission_checks = re.findall(r'check_permission\(["\']([^"\']*)["\']', content)
        
        for permission in permission_checks:
            if permission in self.critical_permissions:
                self.add_security_pass(f"{file_path}: Critical permission check found: {permission}")
            else:
                self.add_security_pass(f"{file_path}: Permission check found: {permission}")
        
        # Look for role checks
        role_checks = re.findall(r'current_user\.has_role\(["\']([^"\']*)["\']', content)
        
        for role in role_checks:
            if role in self.role_hierarchy:
                self.add_security_pass(f"{file_path}: Role check found: {role}")
            else:
                self.add_security_issue(f"{file_path}: Unknown role in check: {role}")
    
    def test_role_visibility(self, file_path: Path, content: str):
        """Test for proper role-based visibility"""
        
        # Look for RBAC classes
        rbac_classes = re.findall(r'nvc-rbac-([a-z-]+)', content)
        
        for rbac_class in rbac_classes:
            if rbac_class in ['admin-only', 'manager-plus', 'treasury-only', 'compliance-only']:
                self.add_security_pass(f"{file_path}: RBAC visibility class found: {rbac_class}")
            else:
                self.add_security_issue(f"{file_path}: Unknown RBAC class: {rbac_class}")
        
        # Look for data-required-role attributes
        role_attributes = re.findall(r'data-required-role=["\']([^"\']*)["\']', content)
        
        for role in role_attributes:
            if role in self.role_hierarchy:
                self.add_security_pass(f"{file_path}: Role requirement found: {role}")
            else:
                self.add_security_issue(f"{file_path}: Unknown role requirement: {role}")
    
    def test_data_exposure(self, file_path: Path, content: str):
        """Test for potential data exposure"""
        
        # Look for sensitive data that might be exposed
        sensitive_patterns = [
            r'password',
            r'secret',
            r'key',
            r'token',
            r'ssn',
            r'social_security',
            r'credit_card',
            r'account_number'
        ]
        
        for pattern in sensitive_patterns:
            matches = re.findall(f'{pattern}[^a-zA-Z]', content, re.IGNORECASE)
            
            for match in matches:
                # Check if it's in a comment or safe context
                if '<!--' in match or 'placeholder' in match.lower():
                    continue
                
                # Check if it's properly protected
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if match in line:
                        if 'if current_user' in line or 'check_permission' in line:
                            self.add_security_pass(f"{file_path}: Protected sensitive data: {pattern}")
                        else:
                            self.add_security_issue(f"{file_path}: Potentially exposed sensitive data: {pattern}")
    
    def test_csrf_protection(self, file_path: Path, content: str):
        """Test for CSRF protection in forms"""
        
        # Look for forms
        forms = re.findall(r'<form[^>]*>', content, re.IGNORECASE)
        
        for form in forms:
            if 'method="post"' in form.lower() or 'method=\'post\'' in form.lower():
                # Check if CSRF token is present in the template
                if 'csrf' not in content.lower():
                    self.add_security_issue(f"{file_path}: POST form without CSRF protection")
                else:
                    self.add_security_pass(f"{file_path}: POST form with CSRF protection")
    
    def test_javascript_security(self):
        """Test JavaScript files for security issues"""
        print("⚡ Testing JavaScript Security...")
        
        js_files = list(self.base_path.rglob("*.js"))
        
        for js_file in js_files:
            if self.should_skip_file(js_file):
                continue
                
            try:
                content = js_file.read_text(encoding='utf-8')
                self.test_js_security(js_file, content)
            except Exception as e:
                self.add_security_issue(f"Failed to read JS {js_file}: {e}")
        
        print(f"   ✅ Tested {len([f for f in js_files if not self.should_skip_file(f)])} JavaScript files")
    
    def test_js_security(self, file_path: Path, content: str):
        """Test individual JavaScript file for security"""
        
        # Test for permission checks in JavaScript
        if 'checkPermission' in content or 'check_permission' in content:
            self.add_security_pass(f"{file_path}: Permission checks in JavaScript")
        
        # Test for role checks
        if 'checkRole' in content or 'userRole' in content:
            self.add_security_pass(f"{file_path}: Role checks in JavaScript")
        
        # Test for security logging
        if 'logSecurityEvent' in content or 'audit' in content:
            self.add_security_pass(f"{file_path}: Security logging implemented")
        
        # Test for XSS prevention
        if 'innerHTML' in content and 'sanitize' not in content:
            self.add_security_issue(f"{file_path}: Potential XSS vulnerability with innerHTML")
        
        # Test for eval usage (dangerous)
        if 'eval(' in content:
            self.add_security_issue(f"{file_path}: Dangerous eval() usage found")
    
    def test_css_security(self):
        """Test CSS files for security-related styling"""
        print("🎨 Testing CSS Security...")
        
        css_files = list(self.base_path.rglob("*.css"))
        
        for css_file in css_files:
            if self.should_skip_file(css_file):
                continue
                
            try:
                content = css_file.read_text(encoding='utf-8')
                self.test_css_file_security(css_file, content)
            except Exception as e:
                self.add_security_issue(f"Failed to read CSS {css_file}: {e}")
        
        print(f"   ✅ Tested {len([f for f in css_files if not self.should_skip_file(f)])} CSS files")
    
    def test_css_file_security(self, file_path: Path, content: str):
        """Test individual CSS file for security"""
        
        # Test for RBAC styling
        if 'nvc-rbac' in content:
            self.add_security_pass(f"{file_path}: RBAC styling implemented")
        
        # Test for role-based visibility
        if 'data-user-role' in content:
            self.add_security_pass(f"{file_path}: Role-based styling found")
        
        # Test for security indicators
        if 'compliance' in content or 'finra' in content:
            self.add_security_pass(f"{file_path}: Security/compliance styling found")
    
    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            'node_modules',
            '.git',
            '__pycache__',
            '.pytest_cache',
            'vendor',
            'bootstrap',
            'jquery',
            'venv',
            'site-packages'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def add_security_issue(self, issue: str):
        """Add a security issue"""
        self.security_issues.append(issue)
    
    def add_security_pass(self, passed: str):
        """Add a security pass"""
        self.security_passes.append(passed)
    
    def generate_security_report(self) -> Dict:
        """Generate security test report"""
        total_tests = len(self.security_passes) + len(self.security_issues)
        pass_rate = (len(self.security_passes) / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'total_security_tests': total_tests,
            'security_passes': len(self.security_passes),
            'security_issues': len(self.security_issues),
            'security_score': round(pass_rate, 2),
            'issues': self.security_issues,
            'passes': self.security_passes[:20]  # Show first 20 passes
        }
        
        print("\n" + "=" * 50)
        print("🛡️  RBAC SECURITY TEST RESULTS")
        print("=" * 50)
        print(f"Total Security Tests: {report['total_security_tests']}")
        print(f"Security Passes: {report['security_passes']}")
        print(f"Security Issues: {report['security_issues']}")
        print(f"Security Score: {report['security_score']}%")
        
        if report['security_issues'] == 0:
            print("\n✅ All security tests passed!")
        else:
            print(f"\n⚠️  Found {report['security_issues']} security issues:")
            for i, issue in enumerate(report['issues'][:10], 1):
                print(f"   {i}. {issue}")
            
            if len(report['issues']) > 10:
                print(f"   ... and {len(report['issues']) - 10} more issues")
        
        return report

def main():
    """Main function"""
    tester = RBACSecurityTester()
    report = tester.run_security_tests()
    
    # Save report to file
    with open('rbac_security_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Full security report saved to rbac_security_report.json")
    
    # Return exit code based on results
    return 0 if report['security_issues'] == 0 else 1

if __name__ == "__main__":
    exit(main())

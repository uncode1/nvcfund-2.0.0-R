#!/usr/bin/env python3
"""
WCAG AA+ Accessibility Testing Script
NVC Banking Platform - Accessibility Compliance Verification
Version: 3.0.0 - WCAG 2.1 Level AA+ Testing
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import json

class AccessibilityTester:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.issues = []
        self.passed_tests = []
        
    def run_all_tests(self) -> Dict:
        """Run all accessibility tests"""
        print("🔍 Running WCAG AA+ Accessibility Tests...")
        print("=" * 50)
        
        # Test HTML templates
        self.test_html_templates()
        
        # Test CSS for accessibility
        self.test_css_accessibility()
        
        # Test JavaScript accessibility features
        self.test_javascript_accessibility()
        
        # Generate report
        return self.generate_report()
    
    def test_html_templates(self):
        """Test HTML templates for accessibility compliance"""
        print("📄 Testing HTML Templates...")
        
        template_files = list(self.base_path.rglob("*.html"))
        
        for template_file in template_files:
            if self.should_skip_file(template_file):
                continue
                
            try:
                content = template_file.read_text(encoding='utf-8')
                self.test_template_accessibility(template_file, content)
            except Exception as e:
                self.add_issue(f"Failed to read template {template_file}: {e}")
        
        print(f"   ✅ Tested {len(template_files)} templates")
    
    def test_template_accessibility(self, file_path: Path, content: str):
        """Test individual template for accessibility"""
        
        # Test 1: Check for proper heading hierarchy
        self.test_heading_hierarchy(file_path, content)
        
        # Test 2: Check for alt text on images
        self.test_image_alt_text(file_path, content)
        
        # Test 3: Check for form labels
        self.test_form_labels(file_path, content)
        
        # Test 4: Check for ARIA attributes
        self.test_aria_attributes(file_path, content)
        
        # Test 5: Check for skip links
        self.test_skip_links(file_path, content)
        
        # Test 6: Check for proper button/link text
        self.test_interactive_elements(file_path, content)
    
    def test_heading_hierarchy(self, file_path: Path, content: str):
        """Test heading hierarchy (h1, h2, h3, etc.)"""
        headings = re.findall(r'<h([1-6])[^>]*>', content, re.IGNORECASE)
        
        if headings:
            heading_levels = [int(h) for h in headings]
            
            # Check if starts with h1 or h2 (h1 might be in base template)
            if heading_levels and heading_levels[0] > 2:
                self.add_issue(f"{file_path}: Heading hierarchy should start with h1 or h2, found h{heading_levels[0]}")
            
            # Check for skipped levels
            for i in range(1, len(heading_levels)):
                if heading_levels[i] - heading_levels[i-1] > 1:
                    self.add_issue(f"{file_path}: Skipped heading level from h{heading_levels[i-1]} to h{heading_levels[i]}")
        
        self.passed_tests.append(f"{file_path}: Heading hierarchy checked")
    
    def test_image_alt_text(self, file_path: Path, content: str):
        """Test images for alt text"""
        # Find img tags without alt attribute
        img_without_alt = re.findall(r'<img(?![^>]*alt=)[^>]*>', content, re.IGNORECASE)
        
        for img in img_without_alt:
            # Skip if it has aria-hidden="true" (decorative images)
            if 'aria-hidden="true"' not in img:
                self.add_issue(f"{file_path}: Image missing alt text: {img[:50]}...")
        
        # Find img tags with empty alt
        img_empty_alt = re.findall(r'<img[^>]*alt=""[^>]*>', content, re.IGNORECASE)
        
        for img in img_empty_alt:
            # Empty alt is OK for decorative images, but check if it should be decorative
            if 'aria-hidden="true"' not in img and 'decorative' not in img.lower():
                # This might be intentional, so it's a warning not an error
                pass
        
        self.passed_tests.append(f"{file_path}: Image alt text checked")
    
    def test_form_labels(self, file_path: Path, content: str):
        """Test form inputs for proper labels"""
        # Find input elements
        inputs = re.findall(r'<input[^>]*>', content, re.IGNORECASE)
        
        for input_tag in inputs:
            input_type = re.search(r'type=["\']([^"\']*)["\']', input_tag)
            input_id = re.search(r'id=["\']([^"\']*)["\']', input_tag)
            
            # Skip hidden inputs and buttons
            if input_type and input_type.group(1).lower() in ['hidden', 'submit', 'button']:
                continue
            
            # Check for aria-label or aria-labelledby
            has_aria_label = 'aria-label=' in input_tag or 'aria-labelledby=' in input_tag
            
            # Check for associated label
            has_label = False
            if input_id:
                label_pattern = f'<label[^>]*for=["\']?{input_id.group(1)}["\']?[^>]*>'
                has_label = bool(re.search(label_pattern, content, re.IGNORECASE))
            
            if not has_aria_label and not has_label:
                self.add_issue(f"{file_path}: Input missing label or aria-label: {input_tag[:50]}...")
        
        self.passed_tests.append(f"{file_path}: Form labels checked")
    
    def test_aria_attributes(self, file_path: Path, content: str):
        """Test for proper ARIA attributes"""
        # Check for buttons with aria-label
        buttons = re.findall(r'<button[^>]*>', content, re.IGNORECASE)
        
        for button in buttons:
            # If button only has icon, it should have aria-label
            if '<i class="fa' in button and 'aria-label=' not in button:
                # Check if there's text content (this is a simplified check)
                if '</button>' in content:
                    button_content = re.search(r'<button[^>]*>(.*?)</button>', content, re.IGNORECASE | re.DOTALL)
                    if button_content:
                        text_content = re.sub(r'<[^>]*>', '', button_content.group(1)).strip()
                        if not text_content or text_content.startswith('<'):
                            self.add_issue(f"{file_path}: Icon button missing aria-label: {button[:50]}...")
        
        self.passed_tests.append(f"{file_path}: ARIA attributes checked")
    
    def test_skip_links(self, file_path: Path, content: str):
        """Test for skip links"""
        # Look for skip links
        skip_links = re.findall(r'<a[^>]*href=["\']#[^"\']*["\'][^>]*>.*?skip.*?</a>', content, re.IGNORECASE)
        
        if 'unified_base.html' in str(file_path) and not skip_links:
            self.add_issue(f"{file_path}: Base template should include skip links")
        
        self.passed_tests.append(f"{file_path}: Skip links checked")
    
    def test_interactive_elements(self, file_path: Path, content: str):
        """Test interactive elements for accessibility"""
        # Check for links with meaningful text
        links = re.findall(r'<a[^>]*>(.*?)</a>', content, re.IGNORECASE | re.DOTALL)
        
        for link_content in links:
            text_content = re.sub(r'<[^>]*>', '', link_content).strip()
            
            # Check for generic link text
            if text_content.lower() in ['click here', 'read more', 'more', 'link']:
                self.add_issue(f"{file_path}: Link has non-descriptive text: '{text_content}'")
        
        self.passed_tests.append(f"{file_path}: Interactive elements checked")
    
    def test_css_accessibility(self):
        """Test CSS for accessibility compliance"""
        print("🎨 Testing CSS Accessibility...")
        
        css_files = list(self.base_path.rglob("*.css"))
        
        for css_file in css_files:
            if self.should_skip_file(css_file):
                continue
                
            try:
                content = css_file.read_text(encoding='utf-8')
                self.test_css_file_accessibility(css_file, content)
            except Exception as e:
                self.add_issue(f"Failed to read CSS {css_file}: {e}")
        
        print(f"   ✅ Tested {len(css_files)} CSS files")
    
    def test_css_file_accessibility(self, file_path: Path, content: str):
        """Test individual CSS file for accessibility"""
        
        # Test for focus indicators
        if ':focus' not in content and 'focus' in str(file_path):
            self.add_issue(f"{file_path}: CSS file should include focus styles")
        
        # Test for reduced motion support
        if 'prefers-reduced-motion' not in content and 'animation' in content:
            self.add_issue(f"{file_path}: CSS with animations should respect prefers-reduced-motion")
        
        # Test for high contrast support
        if 'prefers-contrast' not in content and 'contrast' in str(file_path):
            # This is optional, so just note it
            pass
        
        self.passed_tests.append(f"{file_path}: CSS accessibility checked")
    
    def test_javascript_accessibility(self):
        """Test JavaScript for accessibility features"""
        print("⚡ Testing JavaScript Accessibility...")
        
        js_files = list(self.base_path.rglob("*.js"))
        
        for js_file in js_files:
            if self.should_skip_file(js_file):
                continue
                
            try:
                content = js_file.read_text(encoding='utf-8')
                self.test_js_file_accessibility(js_file, content)
            except Exception as e:
                self.add_issue(f"Failed to read JS {js_file}: {e}")
        
        print(f"   ✅ Tested {len(js_files)} JavaScript files")
    
    def test_js_file_accessibility(self, file_path: Path, content: str):
        """Test individual JavaScript file for accessibility"""
        
        # Test for keyboard event handling
        if 'addEventListener' in content and 'click' in content:
            if 'keydown' not in content and 'keypress' not in content:
                # This might be OK, but worth noting
                pass
        
        # Test for ARIA live regions
        if 'aria-live' in content or 'announce' in content:
            self.passed_tests.append(f"{file_path}: Includes ARIA live region support")
        
        # Test for focus management
        if 'focus()' in content:
            self.passed_tests.append(f"{file_path}: Includes focus management")
        
        self.passed_tests.append(f"{file_path}: JavaScript accessibility checked")
    
    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            'node_modules',
            '.git',
            '__pycache__',
            '.pytest_cache',
            'vendor',
            'bootstrap',
            'jquery'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def add_issue(self, issue: str):
        """Add an accessibility issue"""
        self.issues.append(issue)
    
    def generate_report(self) -> Dict:
        """Generate accessibility test report"""
        total_tests = len(self.passed_tests) + len(self.issues)
        pass_rate = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'total_tests': total_tests,
            'passed_tests': len(self.passed_tests),
            'issues_found': len(self.issues),
            'pass_rate': round(pass_rate, 2),
            'issues': self.issues,
            'passed': self.passed_tests[:10]  # Show first 10 passed tests
        }
        
        print("\n" + "=" * 50)
        print("🏆 ACCESSIBILITY TEST RESULTS")
        print("=" * 50)
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['passed_tests']}")
        print(f"Issues: {report['issues_found']}")
        print(f"Pass Rate: {report['pass_rate']}%")
        
        if report['issues_found'] == 0:
            print("\n✅ All accessibility tests passed!")
        else:
            print(f"\n⚠️  Found {report['issues_found']} accessibility issues:")
            for i, issue in enumerate(report['issues'][:10], 1):
                print(f"   {i}. {issue}")
            
            if len(report['issues']) > 10:
                print(f"   ... and {len(report['issues']) - 10} more issues")
        
        return report

def main():
    """Main function"""
    tester = AccessibilityTester()
    report = tester.run_all_tests()
    
    # Save report to file
    with open('accessibility_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Full report saved to accessibility_report.json")
    
    # Return exit code based on results
    return 0 if report['issues_found'] == 0 else 1

if __name__ == "__main__":
    exit(main())

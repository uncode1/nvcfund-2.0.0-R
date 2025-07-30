#!/usr/bin/env python3
"""
Template Consistency Checker for NVC Banking Platform
Ensures all templates follow unified template system standards
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
import json
import shutil

class TemplateConsistencyChecker:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.issues = []
        self.fixes = []
        
        # Required patterns for unified templates
        self.unified_patterns = {
            'base_template': r'{%\s*extends\s+["\']unified_base\.html["\']',
            'navigation_import': r'{%\s*from\s+["\']components/unified_navigation\.html["\']',
            'forms_import': r'{%\s*from\s+["\']components/unified_forms\.html["\']',
            'unified_css': r'unified-template-system\.css',
            'unified_js': r'unified-interactions\.js'
        }
        
        # Legacy patterns that should be replaced
        self.legacy_patterns = {
            'old_base': [r'{%\s*extends\s+["\']base\.html["\']', r'{%\s*extends\s+["\']layout\.html["\']'],
            'old_css': [r'bootstrap\.css', r'legacy\.css', r'old-style\.css'],
            'old_js': [r'jquery\.js', r'legacy\.js', r'old-script\.js'],
            'inline_onclick': r'onclick\s*=',
            'inline_style': r'style\s*=\s*["\'][^"\']{20,}["\']'  # Long inline styles
        }
    
    def check_all(self) -> Dict:
        """Check all templates for consistency"""
        print("🔍 Starting template consistency check...")
        
        template_files = list(self.root_path.rglob("*.html"))
        
        for file_path in template_files:
            self.check_file(file_path)
        
        return self.generate_report()
    
    def check_file(self, file_path: Path):
        """Check a single template file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_issues = []
            relative_path = str(file_path.relative_to(self.root_path))
            
            # Check for unified template compliance
            self.check_unified_compliance(content, relative_path, file_issues)
            
            # Check for legacy patterns
            self.check_legacy_patterns(content, relative_path, file_issues)
            
            # Check template structure
            self.check_template_structure(content, relative_path, file_issues)
            
            # Check for missing components
            self.check_missing_components(content, relative_path, file_issues)
            
            if file_issues:
                self.issues.append({
                    'file': relative_path,
                    'issues': file_issues
                })
                
        except Exception as e:
            print(f"Error checking {file_path}: {e}")
    
    def check_unified_compliance(self, content: str, file_path: str, issues: List):
        """Check if template follows unified system"""
        
        # Skip certain files that don't need to extend unified_base
        skip_files = ['unified_base.html', 'components/', 'errors/', 'email/']
        if any(skip in file_path for skip in skip_files):
            return
        
        # Check if extends unified_base.html
        if not re.search(self.unified_patterns['base_template'], content):
            issues.append({
                'type': 'missing_unified_base',
                'severity': 'high',
                'message': 'Template does not extend unified_base.html',
                'fix': 'Add {% extends "unified_base.html" %} at the top'
            })
        
        # Check for unified CSS inclusion
        if 'css' in content and not re.search(self.unified_patterns['unified_css'], content):
            issues.append({
                'type': 'missing_unified_css',
                'severity': 'medium',
                'message': 'Template does not include unified-template-system.css',
                'fix': 'Include unified CSS in template or base template'
            })
        
        # Check for unified JS inclusion
        if 'javascript' in content.lower() and not re.search(self.unified_patterns['unified_js'], content):
            issues.append({
                'type': 'missing_unified_js',
                'severity': 'medium',
                'message': 'Template does not include unified-interactions.js',
                'fix': 'Include unified JavaScript in template or base template'
            })
    
    def check_legacy_patterns(self, content: str, file_path: str, issues: List):
        """Check for legacy patterns that should be updated"""
        
        # Check for old base templates
        for pattern in self.legacy_patterns['old_base']:
            if re.search(pattern, content):
                issues.append({
                    'type': 'legacy_base_template',
                    'severity': 'high',
                    'message': 'Uses legacy base template',
                    'fix': 'Replace with {% extends "unified_base.html" %}'
                })
        
        # Check for old CSS files
        for pattern in self.legacy_patterns['old_css']:
            if re.search(pattern, content):
                issues.append({
                    'type': 'legacy_css',
                    'severity': 'medium',
                    'message': f'Uses legacy CSS: {pattern}',
                    'fix': 'Replace with unified CSS system'
                })
        
        # Check for old JS files
        for pattern in self.legacy_patterns['old_js']:
            if re.search(pattern, content):
                issues.append({
                    'type': 'legacy_js',
                    'severity': 'medium',
                    'message': f'Uses legacy JavaScript: {pattern}',
                    'fix': 'Replace with unified JavaScript system'
                })
        
        # Check for onclick handlers
        if re.search(self.legacy_patterns['inline_onclick'], content):
            onclick_count = len(re.findall(self.legacy_patterns['inline_onclick'], content))
            issues.append({
                'type': 'onclick_handlers',
                'severity': 'high',
                'message': f'Contains {onclick_count} onclick handlers',
                'fix': 'Convert to data-action pattern using legacy_pattern_migrator.py'
            })
        
        # Check for long inline styles
        if re.search(self.legacy_patterns['inline_style'], content):
            style_count = len(re.findall(self.legacy_patterns['inline_style'], content))
            issues.append({
                'type': 'inline_styles',
                'severity': 'medium',
                'message': f'Contains {style_count} long inline styles',
                'fix': 'Extract to CSS classes using inline_style_extractor.py'
            })
    
    def check_template_structure(self, content: str, file_path: str, issues: List):
        """Check template structure and syntax"""
        
        # Check for proper block structure
        block_starts = re.findall(r'{%\s*block\s+(\w+)\s*%}', content)
        block_ends = re.findall(r'{%\s*endblock\s*(?:\s+(\w+))?\s*%}', content)
        
        if len(block_starts) != len(block_ends):
            issues.append({
                'type': 'block_mismatch',
                'severity': 'high',
                'message': f'Block mismatch: {len(block_starts)} starts, {len(block_ends)} ends',
                'fix': 'Add missing {% endblock %} tags'
            })
        
        # Check for common template errors
        common_errors = [
            (r'{%\s*end\s*%}', 'Invalid {% end %} tag'),
            (r'{{[^}]*{[^}]*}}', 'Nested template variables'),
            (r'{%[^%]*{%', 'Nested template tags'),
        ]
        
        for pattern, message in common_errors:
            if re.search(pattern, content):
                issues.append({
                    'type': 'syntax_error',
                    'severity': 'high',
                    'message': message,
                    'fix': 'Fix template syntax'
                })
    
    def check_missing_components(self, content: str, file_path: str, issues: List):
        """Check for missing unified components that should be used"""
        
        # Skip component files themselves
        if 'components/' in file_path:
            return
        
        # Check for forms that should use unified form components
        if '<form' in content and 'unified_forms' not in content:
            issues.append({
                'type': 'missing_form_components',
                'severity': 'low',
                'message': 'Form found but not using unified form components',
                'fix': 'Consider using unified form macros'
            })
        
        # Check for navigation that should use unified navigation
        nav_patterns = ['<nav', 'navbar', 'menu']
        if any(pattern in content.lower() for pattern in nav_patterns) and 'unified_navigation' not in content:
            issues.append({
                'type': 'missing_navigation_components',
                'severity': 'low',
                'message': 'Navigation found but not using unified navigation components',
                'fix': 'Consider using unified navigation macros'
            })
        
        # Check for cards that should use unified card system
        if '<div class="card"' in content and 'unified_card_system' not in content:
            issues.append({
                'type': 'missing_card_components',
                'severity': 'low',
                'message': 'Cards found but not using unified card components',
                'fix': 'Consider using unified card macros'
            })
    
    def auto_fix(self, dry_run: bool = True) -> Dict:
        """Automatically fix common issues"""
        print(f"🔧 {'Simulating' if dry_run else 'Applying'} automatic fixes...")
        
        fixes_applied = []
        
        for issue_group in self.issues:
            file_path = self.root_path / issue_group['file']
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                file_fixes = []
                
                for issue in issue_group['issues']:
                    if issue['type'] == 'legacy_base_template':
                        # Replace legacy base template
                        content = re.sub(
                            r'{%\s*extends\s+["\'](?:base|layout)\.html["\']',
                            '{% extends "unified_base.html" %}',
                            content
                        )
                        file_fixes.append('Fixed legacy base template')
                    
                    elif issue['type'] == 'block_mismatch':
                        # Add missing endblock tags
                        block_starts = re.findall(r'{%\s*block\s+(\w+)\s*%}', content)
                        block_ends = re.findall(r'{%\s*endblock\s*(?:\s+(\w+))?\s*%}', content)
                        
                        if len(block_starts) > len(block_ends):
                            # Add missing endblock at the end
                            content += '\n{% endblock %}'
                            file_fixes.append('Added missing endblock tag')
                    
                    elif issue['type'] == 'legacy_css':
                        # Replace legacy CSS references
                        content = re.sub(
                            r'bootstrap\.css',
                            'unified-template-system.css',
                            content
                        )
                        file_fixes.append('Updated CSS references')
                
                if content != original_content:
                    if not dry_run:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                    
                    fixes_applied.append({
                        'file': issue_group['file'],
                        'fixes': file_fixes
                    })
                    
                    print(f"{'Would fix' if dry_run else 'Fixed'}: {issue_group['file']}")
                
            except Exception as e:
                print(f"Error fixing {file_path}: {e}")
        
        return {
            'fixes_applied': fixes_applied,
            'dry_run': dry_run
        }
    
    def generate_report(self) -> Dict:
        """Generate consistency report"""
        total_files = len(self.issues)
        total_issues = sum(len(issue_group['issues']) for issue_group in self.issues)
        
        # Categorize issues by severity
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        for issue_group in self.issues:
            for issue in issue_group['issues']:
                severity_counts[issue['severity']] += 1
        
        report = {
            'summary': {
                'files_with_issues': total_files,
                'total_issues': total_issues,
                'severity_breakdown': severity_counts
            },
            'issues': self.issues,
            'recommendations': [
                "Fix high-severity issues first (template structure, legacy patterns)",
                "Run auto-fix to resolve common issues automatically",
                "Update templates to use unified components",
                "Test all pages after making changes"
            ]
        }
        
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Check template consistency')
    parser.add_argument('--fix', action='store_true', help='Apply automatic fixes')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without applying')
    
    args = parser.parse_args()
    
    checker = TemplateConsistencyChecker()
    
    if args.fix or args.dry_run:
        fix_report = checker.auto_fix(dry_run=args.dry_run)
        
        with open('template_fixes_report.json', 'w') as f:
            json.dump(fix_report, f, indent=2)
        
        print(f"\n📄 Fix report saved to: template_fixes_report.json")
        return
    
    # Run consistency check
    report = checker.check_all()
    
    # Save report
    with open('template_consistency_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEMPLATE CONSISTENCY SUMMARY")
    print("="*60)
    
    summary = report['summary']
    print(f"📁 Files with issues: {summary['files_with_issues']}")
    print(f"⚠️  Total issues: {summary['total_issues']}")
    print(f"🔴 High severity: {summary['severity_breakdown']['high']}")
    print(f"🟡 Medium severity: {summary['severity_breakdown']['medium']}")
    print(f"🟢 Low severity: {summary['severity_breakdown']['low']}")
    
    print("\n📋 RECOMMENDATIONS:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print(f"\n📄 Full report saved to: template_consistency_report.json")
    print("\n🔧 To apply automatic fixes, run:")
    print("python template_consistency_checker.py --fix")

if __name__ == "__main__":
    main()

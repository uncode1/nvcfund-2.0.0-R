#!/usr/bin/env python3
"""
Code Quality Analyzer for NVC Banking Platform
Identifies legacy patterns, inline styles, and template inconsistencies
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class CodeQualityAnalyzer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
        
    def analyze_all(self) -> Dict:
        """Run comprehensive code quality analysis"""
        print("🔍 Starting comprehensive code quality analysis...")
        
        # Analyze different file types
        self.analyze_onclick_handlers()
        self.analyze_inline_styles()
        self.analyze_template_consistency()
        self.analyze_javascript_patterns()
        self.analyze_css_duplication()
        
        return self.generate_report()
    
    def analyze_onclick_handlers(self):
        """Find and analyze onclick handlers in templates"""
        print("📋 Analyzing onclick handlers...")
        
        onclick_pattern = re.compile(r'onclick\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
        template_files = list(self.root_path.rglob("*.html"))
        
        for file_path in template_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                matches = onclick_pattern.findall(content)
                if matches:
                    self.issues['onclick_handlers'].append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'count': len(matches),
                        'handlers': matches
                    })
                    self.stats['onclick_files'] += 1
                    self.stats['onclick_total'] += len(matches)
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def analyze_inline_styles(self):
        """Find and analyze inline styles in templates"""
        print("🎨 Analyzing inline styles...")
        
        style_pattern = re.compile(r'style\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
        template_files = list(self.root_path.rglob("*.html"))
        
        for file_path in template_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                matches = style_pattern.findall(content)
                if matches:
                    # Filter out simple styles that should remain inline
                    significant_styles = [s for s in matches if len(s) > 20 or ';' in s]
                    
                    if significant_styles:
                        self.issues['inline_styles'].append({
                            'file': str(file_path.relative_to(self.root_path)),
                            'count': len(significant_styles),
                            'styles': significant_styles[:5]  # Show first 5
                        })
                        self.stats['inline_style_files'] += 1
                        self.stats['inline_styles_total'] += len(significant_styles)
                        
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def analyze_template_consistency(self):
        """Check template consistency with unified system"""
        print("📄 Analyzing template consistency...")
        
        template_files = list(self.root_path.rglob("*.html"))
        unified_patterns = [
            r'unified_base\.html',
            r'unified_navigation\.html',
            r'unified_forms\.html',
            r'unified-template-system\.css',
            r'unified-interactions\.js'
        ]
        
        for file_path in template_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check if template extends unified base
                extends_unified = bool(re.search(r'{%\s*extends\s+["\']unified_base\.html["\']', content))
                uses_unified_components = any(re.search(pattern, content) for pattern in unified_patterns)
                
                # Check for legacy patterns
                has_legacy_css = bool(re.search(r'bootstrap\.css|legacy\.css|old-style\.css', content))
                has_legacy_js = bool(re.search(r'jquery\.js|legacy\.js|old-script\.js', content))
                
                if not extends_unified and 'base' in file_path.name.lower():
                    self.issues['template_consistency'].append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'issue': 'Does not extend unified_base.html',
                        'severity': 'high'
                    })
                
                if has_legacy_css or has_legacy_js:
                    self.issues['template_consistency'].append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'issue': 'Uses legacy CSS/JS files',
                        'severity': 'medium'
                    })
                    
                if not uses_unified_components and len(content) > 1000:
                    self.issues['template_consistency'].append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'issue': 'Large template not using unified components',
                        'severity': 'low'
                    })
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def analyze_javascript_patterns(self):
        """Analyze JavaScript for legacy patterns"""
        print("⚡ Analyzing JavaScript patterns...")
        
        js_files = list(self.root_path.rglob("*.js"))
        legacy_patterns = [
            (r'\$\(document\)\.ready', 'jQuery document ready (use DOMContentLoaded)'),
            (r'var\s+\w+\s*=', 'var declarations (use let/const)'),
            (r'function\s+\w+\s*\(', 'function declarations (consider arrow functions)'),
            (r'\.innerHTML\s*=', 'innerHTML usage (consider safer alternatives)'),
            (r'eval\s*\(', 'eval usage (security risk)')
        ]
        
        for file_path in js_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                file_issues = []
                for pattern, description in legacy_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        file_issues.append({
                            'pattern': description,
                            'count': len(matches)
                        })
                
                if file_issues:
                    self.issues['javascript_patterns'].append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'issues': file_issues
                    })
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def analyze_css_duplication(self):
        """Find CSS duplication and optimization opportunities"""
        print("🎨 Analyzing CSS duplication...")
        
        css_files = list(self.root_path.rglob("*.css"))
        css_rules = defaultdict(list)
        
        for file_path in css_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Simple CSS rule extraction
                rules = re.findall(r'([.#][\w-]+)\s*{([^}]*)}', content)
                for selector, properties in rules:
                    css_rules[selector.strip()].append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'properties': properties.strip()
                    })
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        # Find duplicated selectors
        duplicated = {selector: files for selector, files in css_rules.items() if len(files) > 1}
        
        if duplicated:
            self.issues['css_duplication'] = [
                {
                    'selector': selector,
                    'files': [f['file'] for f in files],
                    'count': len(files)
                }
                for selector, files in list(duplicated.items())[:10]  # Show top 10
            ]
    
    def generate_report(self) -> Dict:
        """Generate comprehensive quality report"""
        report = {
            'summary': {
                'onclick_handlers': {
                    'files': self.stats.get('onclick_files', 0),
                    'total_handlers': self.stats.get('onclick_total', 0)
                },
                'inline_styles': {
                    'files': self.stats.get('inline_style_files', 0),
                    'total_styles': self.stats.get('inline_styles_total', 0)
                },
                'template_consistency_issues': len(self.issues.get('template_consistency', [])),
                'javascript_pattern_files': len(self.issues.get('javascript_patterns', [])),
                'css_duplication_selectors': len(self.issues.get('css_duplication', []))
            },
            'issues': dict(self.issues),
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if self.stats.get('onclick_total', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'Legacy Patterns',
                'title': 'Migrate onclick handlers to data-action pattern',
                'description': f"Found {self.stats['onclick_total']} onclick handlers in {self.stats['onclick_files']} files",
                'action': 'Run legacy_pattern_migrator.py to automatically convert onclick to data-action'
            })
        
        if self.stats.get('inline_styles_total', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'CSS Optimization',
                'title': 'Extract inline styles to CSS classes',
                'description': f"Found {self.stats['inline_styles_total']} inline styles in {self.stats['inline_style_files']} files",
                'action': 'Run inline_style_extractor.py to move styles to CSS files'
            })
        
        if len(self.issues.get('template_consistency', [])) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'Template Consistency',
                'title': 'Update templates to use unified system',
                'description': f"Found {len(self.issues['template_consistency'])} template consistency issues",
                'action': 'Run template_consistency_checker.py to fix template inheritance'
            })
        
        return recommendations

def main():
    analyzer = CodeQualityAnalyzer()
    report = analyzer.analyze_all()
    
    # Save report
    with open('code_quality_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 CODE QUALITY ANALYSIS SUMMARY")
    print("="*60)
    
    summary = report['summary']
    print(f"🖱️  Onclick Handlers: {summary['onclick_handlers']['total_handlers']} in {summary['onclick_handlers']['files']} files")
    print(f"🎨 Inline Styles: {summary['inline_styles']['total_styles']} in {summary['inline_styles']['files']} files")
    print(f"📄 Template Issues: {summary['template_consistency_issues']} consistency issues")
    print(f"⚡ JavaScript Issues: {summary['javascript_pattern_files']} files with legacy patterns")
    print(f"🔄 CSS Duplication: {summary['css_duplication_selectors']} duplicated selectors")
    
    print("\n📋 RECOMMENDATIONS:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. [{rec['priority'].upper()}] {rec['title']}")
        print(f"   {rec['description']}")
        print(f"   Action: {rec['action']}\n")
    
    print(f"📄 Full report saved to: code_quality_report.json")

if __name__ == "__main__":
    main()

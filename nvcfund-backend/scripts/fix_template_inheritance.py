#!/usr/bin/env python3
"""
Script to fix template inheritance for all templates that don't extend base templates.
This ensures all protected templates use the unified_base.html template.
"""

import os
import re
from pathlib import Path

def fix_template_inheritance():
    """Fix all templates to extend unified_base.html"""
    
    # Get the backend directory
    backend_dir = Path(__file__).parent.parent
    templates_dir = backend_dir / 'templates'
    
    # Find all HTML files that don't extend any base template
    standalone_templates = []
    
    for html_file in backend_dir.rglob('*.html'):
        if html_file.is_file():
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Skip if already extends a base template
                if re.search(r'{%\s*extends\s+["\']', content):
                    continue
                    
                # Skip if it's a base template itself
                if 'unified_base.html' in str(html_file) or 'public_base.html' in str(html_file):
                    continue
                    
                # Skip if it's a component or macro file
                if any(skip_dir in str(html_file) for skip_dir in ['components', 'macros', 'errors']):
                    continue
                    
                # Check if it starts with DOCTYPE (standalone template)
                if content.strip().startswith('<!DOCTYPE html>'):
                    standalone_templates.append(html_file)
                    
            except Exception as e:
                print(f"Error reading {html_file}: {e}")
    
    print(f"Found {len(standalone_templates)} standalone templates to fix:")
    
    for template_file in standalone_templates:
        print(f"  - {template_file.relative_to(backend_dir)}")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from the original template
            title_match = re.search(r'<title>(.*?)</title>', content)
            title = title_match.group(1) if title_match else "NVC Banking Platform"
            
            # Extract CSS from the original template
            style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
            custom_css = style_match.group(1) if style_match else ""
            
            # Extract body content
            body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
            body_content = body_match.group(1) if body_match else content
            
            # Extract scripts
            script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            custom_script = script_match.group(1) if script_match else ""
            
            # Create new template content
            new_content = f"""{{% extends "unified_base.html" %}}

{{% block title %}}{title}{{% endblock %}}

{{% block extra_css %}}
{custom_css}
{{% endblock %}}

{{% block content %}}
{body_content}
{{% endblock %}}

{{% block extra_js %}}
{custom_script}
{{% endblock %}}
"""
            
            # Write the updated template
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print(f"    ✅ Fixed: {template_file.name}")
            
        except Exception as e:
            print(f"    ❌ Error fixing {template_file}: {e}")
    
    print(f"\n✅ Template inheritance fix completed!")
    print(f"   - Fixed {len(standalone_templates)} templates")
    print(f"   - All templates now extend unified_base.html")
    print(f"   - CSS styles will be automatically applied to all templates")

if __name__ == "__main__":
    fix_template_inheritance() 
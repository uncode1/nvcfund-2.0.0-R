#!/usr/bin/env python3
"""
Comprehensive Template Syntax Checker
NVC Banking Platform - Template Validation Tool

This script checks all HTML templates for Jinja2 syntax errors:
1. Missing {% endif %}, {% endfor %}, {% endblock %} tags
2. Malformed template syntax
3. HTML structure outside template blocks
4. Unclosed blocks and tags
"""

import os
import re
from pathlib import Path

def find_html_files(root_dir):
    """Find all HTML template files in the codebase"""
    html_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    return html_files

def check_template_syntax(filepath):
    """Check a single template file for syntax errors"""
    errors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return [f"Error reading file: {e}"]
    
    # Track opening and closing tags
    block_stack = []
    if_stack = []
    for_stack = []
    
    for line_num, line in enumerate(lines, 1):
        # Check for Jinja2 blocks
        
        # Block tags
        block_opens = re.findall(r'{%\s*block\s+(\w+)', line)
        for block_name in block_opens:
            block_stack.append((block_name, line_num))
        
        block_closes = re.findall(r'{%\s*endblock', line)
        for _ in block_closes:
            if block_stack:
                block_stack.pop()
            else:
                errors.append(f"Line {line_num}: Unexpected {{% endblock %}} without matching {{% block %}}")
        
        # If statements
        if_opens = re.findall(r'{%\s*if\s+', line)
        for _ in if_opens:
            if_stack.append(line_num)
        
        if_closes = re.findall(r'{%\s*endif', line)
        for _ in if_closes:
            if if_stack:
                if_stack.pop()
            else:
                errors.append(f"Line {line_num}: Unexpected {{% endif %}} without matching {{% if %}}")

        # For loops
        for_opens = re.findall(r'{%\s*for\s+', line)
        for _ in for_opens:
            for_stack.append(line_num)

        for_closes = re.findall(r'{%\s*endfor', line)
        for _ in for_closes:
            if for_stack:
                for_stack.pop()
            else:
                errors.append(f"Line {line_num}: Unexpected {{% endfor %}} without matching {{% for %}}")

        # Check for malformed Jinja2 syntax
        if '{%' in line and '%}' not in line:
            errors.append(f"Line {line_num}: Malformed Jinja2 tag - missing closing %}}")

        if '{{' in line and '}}' not in line:
            errors.append(f"Line {line_num}: Malformed Jinja2 variable - missing closing }}}}")

    # Check for unclosed blocks
    if block_stack:
        for block_name, line_num in block_stack:
            errors.append(f"Line {line_num}: Unclosed {{% block {block_name} %}} - missing {{% endblock %}}")

    if if_stack:
        for line_num in if_stack:
            errors.append(f"Line {line_num}: Unclosed {{% if %}} - missing {{% endif %}}")

    if for_stack:
        for line_num in for_stack:
            errors.append(f"Line {line_num}: Unclosed {{% for %}} - missing {{% endfor %}}")
    
    # Check for HTML structure outside template blocks (for extending templates)
    if 'extends' in content:
        # This template extends another, check for HTML outside blocks
        in_block = False
        block_depth = 0
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and empty lines
            if line.strip().startswith('{#') or not line.strip():
                continue
            
            # Track block depth
            if '{%' in line and 'block' in line and 'endblock' not in line:
                block_depth += 1
                in_block = True
            elif '{%' in line and 'endblock' in line:
                block_depth -= 1
                if block_depth == 0:
                    in_block = False
            
            # Check for HTML tags outside blocks
            if not in_block and block_depth == 0:
                if re.search(r'<(?!/?(?:html|head|body|meta|title|link|script|style))[a-zA-Z]', line):
                    if not line.strip().startswith('{%') and not line.strip().startswith('{{'):
                        errors.append(f"Line {line_num}: HTML content outside template blocks in extending template")
    
    return errors

def main():
    """Main function to check all templates"""
    print("🔍 COMPREHENSIVE TEMPLATE SYNTAX CHECKER")
    print("=" * 60)
    
    # Find all HTML files
    html_files = find_html_files('.')
    print(f"Found {len(html_files)} HTML template files")
    
    total_errors = 0
    files_with_errors = 0
    
    for filepath in html_files:
        errors = check_template_syntax(filepath)
        
        if errors:
            files_with_errors += 1
            total_errors += len(errors)
            
            print(f"\n❌ {filepath}")
            for error in errors:
                print(f"   {error}")
        else:
            print(f"✅ {filepath}")
    
    print(f"\n" + "=" * 60)
    print(f"📊 SYNTAX CHECK SUMMARY:")
    print(f"   Total files checked: {len(html_files)}")
    print(f"   Files with errors: {files_with_errors}")
    print(f"   Total errors found: {total_errors}")
    
    if total_errors == 0:
        print(f"🎉 ALL TEMPLATES HAVE CORRECT SYNTAX!")
    else:
        print(f"⚠️  {total_errors} syntax errors found in {files_with_errors} files")
        print(f"   Please fix these errors before deployment")
    
    return total_errors == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

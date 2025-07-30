#!/usr/bin/env python3
"""
Script to update all template inheritance to use the new unified_base_template.html
"""

import os
import re
from pathlib import Path

def update_template_inheritance(base_dir):
    """Update all templates to use unified_base_template.html"""
    
    # Patterns to replace
    patterns_to_replace = [
        r'{% extends "enhanced_base_template\.html" %}',
        r'{% extends "professional_base_template\.html" %}', 
        r'{% extends "base\.html" %}',
        r"{% extends 'enhanced_base_template\.html' %}",
        r"{% extends 'professional_base_template\.html' %}",
        r"{% extends 'base\.html' %}"
    ]
    
    replacement = '{% extends "unified_base_template.html" %}'
    
    updated_files = []
    
    # Walk through all template files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = Path(root) / file
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Apply replacements
                    for pattern in patterns_to_replace:
                        content = re.sub(pattern, replacement, content)
                    
                    # Only write if changes were made
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        updated_files.append(str(file_path))
                        print(f"Updated: {file_path}")
                
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return updated_files

if __name__ == "__main__":
    base_dir = "/Users/petersumanu/Documents/GitHub/nvcfund-2.0.0/nvcfund-backend"
    
    print("Starting template inheritance update...")
    updated_files = update_template_inheritance(base_dir)
    
    print(f"\nUpdate completed. {len(updated_files)} files updated:")
    for file_path in updated_files:
        print(f"  - {file_path}")
    
    print(f"\nAll templates now extend 'unified_base_template.html'")
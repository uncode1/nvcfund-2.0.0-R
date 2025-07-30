#!/usr/bin/env python3
"""
Safe script to continue updating template inheritance
Shows which files need updating without automatically changing them
"""

import os
from pathlib import Path

def find_templates_to_update(base_dir):
    """Find all templates that still need updating"""
    
    patterns_to_find = [
        'enhanced_base_template.html',
        'professional_base_template.html', 
        'extends "base.html"',
        "extends 'base.html'"
    ]
    
    templates_to_update = []
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = Path(root) / file
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check first few lines for extends statements
                    first_lines = content.split('\n')[:5]
                    
                    for line in first_lines:
                        for pattern in patterns_to_find:
                            if pattern in line:
                                templates_to_update.append({
                                    'file': str(file_path),
                                    'current_extends': line.strip(),
                                    'suggested_fix': line.replace('enhanced_base_template.html', 'unified_base_template.html')
                                                         .replace('professional_base_template.html', 'unified_base_template.html')
                                                         .replace('base.html', 'unified_base_template.html')
                                })
                                break
                
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")
    
    return templates_to_update

if __name__ == "__main__":
    base_dir = "/Users/petersumanu/Documents/GitHub/nvcfund-2.0.0/nvcfund-backend"
    
    print("🔍 Finding templates that need updating...")
    templates_to_update = find_templates_to_update(base_dir)
    
    print(f"\n📊 Found {len(templates_to_update)} templates that need updating:\n")
    
    for i, template_info in enumerate(templates_to_update, 1):
        rel_path = template_info['file'].replace(base_dir, '.')
        print(f"{i:2d}. {rel_path}")
        print(f"    Current: {template_info['current_extends']}")
        print(f"    Fix to:  {template_info['suggested_fix']}")
        print()
    
    if templates_to_update:
        print("📝 To update these templates:")
        print("   1. Open each file in your editor")
        print("   2. Replace the 'extends' line as suggested")
        print("   3. Test the template works correctly")
        print("   4. Move to the next template")
        print("\n⚠️  Remember to test each template after updating!")
    else:
        print("✅ All templates are already using unified_base_template.html!")
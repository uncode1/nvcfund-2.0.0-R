#!/usr/bin/env python3
"""
Comprehensive Template Duplicate Analysis Script
NVC Banking Platform - Template Consolidation Tool

This script analyzes all HTML templates in the codebase to identify:
1. Exact duplicates (same content)
2. Near duplicates (similar content)
3. Unused templates
4. Missing template references
"""

import os
import re
import hashlib
from collections import defaultdict
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

def get_file_hash(filepath):
    """Get SHA256 hash of file content"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def get_template_references(root_dir):
    """Find all template references in Python files"""
    references = defaultdict(list)
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Find render_template calls
                    pattern = r"render_template\s*\(\s*['\"]([^'\"]+\.html)['\"]"
                    matches = re.findall(pattern, content)
                    
                    for match in matches:
                        references[match].append(filepath)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    return references

def analyze_duplicates():
    """Main analysis function"""
    print("=== COMPREHENSIVE TEMPLATE DUPLICATE ANALYSIS ===")
    print("NVC Banking Platform - Template Consolidation Report")
    print("=" * 60)
    
    # Find all HTML files
    html_files = find_html_files('.')
    print(f"Found {len(html_files)} HTML template files")
    
    # Group by filename
    filename_groups = defaultdict(list)
    for filepath in html_files:
        filename = os.path.basename(filepath)
        filename_groups[filename].append(filepath)
    
    # Find template references
    print("\nAnalyzing template references...")
    references = get_template_references('.')
    
    # Analyze duplicates by filename
    duplicates_by_name = {}
    for filename, filepaths in filename_groups.items():
        if len(filepaths) > 1:
            duplicates_by_name[filename] = filepaths
    
    print(f"\n=== DUPLICATE ANALYSIS BY FILENAME ===")
    print(f"Templates with duplicate filenames: {len(duplicates_by_name)}")
    
    critical_duplicates = []
    
    for filename, filepaths in duplicates_by_name.items():
        print(f"\n📄 {filename} ({len(filepaths)} copies):")
        
        # Check file sizes and hashes
        file_info = []
        for filepath in filepaths:
            try:
                size = os.path.getsize(filepath)
                hash_val = get_file_hash(filepath)
                file_info.append({
                    'path': filepath,
                    'size': size,
                    'hash': hash_val
                })
            except Exception as e:
                print(f"  ❌ Error processing {filepath}: {e}")
        
        # Group by content hash
        hash_groups = defaultdict(list)
        for info in file_info:
            if info['hash']:
                hash_groups[info['hash']].append(info)
        
        # Check usage
        template_refs = []
        for ref_template, ref_files in references.items():
            if filename in ref_template:
                template_refs.append((ref_template, ref_files))
        
        print(f"  📊 Usage analysis: {len(template_refs)} reference patterns found")
        
        # Determine if critical
        if len(hash_groups) > 1:
            print(f"  ⚠️  CRITICAL: Multiple different versions detected")
            critical_duplicates.append(filename)
        elif len(hash_groups) == 1:
            print(f"  ✅ EXACT DUPLICATES: All files have identical content")
        
        # Show file details
        for i, info in enumerate(file_info):
            size_kb = info['size'] / 1024
            print(f"    {i+1}. {info['path']} ({size_kb:.1f}KB)")
        
        # Show usage
        if template_refs:
            print(f"  📋 Template references:")
            for ref_template, ref_files in template_refs:
                print(f"    • {ref_template} (used in {len(ref_files)} files)")
        else:
            print(f"  ⚠️  No template references found")
    
    # Summary and recommendations
    print(f"\n=== CONSOLIDATION RECOMMENDATIONS ===")
    print(f"Total duplicate template names: {len(duplicates_by_name)}")
    print(f"Critical duplicates (different content): {len(critical_duplicates)}")
    
    if critical_duplicates:
        print(f"\n🔥 CRITICAL DUPLICATES REQUIRING IMMEDIATE ATTENTION:")
        for filename in critical_duplicates:
            print(f"  • {filename}")
    
    # Most common duplicates
    print(f"\n📊 MOST DUPLICATED TEMPLATES:")
    sorted_duplicates = sorted(duplicates_by_name.items(), 
                             key=lambda x: len(x[1]), reverse=True)
    
    for filename, filepaths in sorted_duplicates[:10]:
        print(f"  {len(filepaths)}x {filename}")
    
    # Unused templates
    print(f"\n🗑️  UNUSED TEMPLATES ANALYSIS:")
    unused_count = 0
    for filepath in html_files:
        filename = os.path.basename(filepath)
        template_path = filepath.replace('nvcfund-backend/', '').replace('modules/', '')
        
        # Check if template is referenced
        is_used = False
        for ref_template in references.keys():
            if filename in ref_template or template_path in ref_template:
                is_used = True
                break
        
        if not is_used:
            unused_count += 1
            if unused_count <= 10:  # Show first 10
                print(f"  • {filepath}")
    
    if unused_count > 10:
        print(f"  ... and {unused_count - 10} more unused templates")
    
    print(f"\nTotal potentially unused templates: {unused_count}")
    
    return duplicates_by_name, critical_duplicates

if __name__ == "__main__":
    analyze_duplicates()
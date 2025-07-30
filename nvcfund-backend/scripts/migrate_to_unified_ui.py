#!/usr/bin/env python3
"""
NVC Banking Platform - UI Standardization Migration Script
Migrates all templates to use the unified base template and components
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class UIStandardizationMigrator:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.templates_dir = self.base_dir / "nvcfund-backend" / "templates"
        self.modules_dir = self.base_dir / "nvcfund-backend" / "modules"
        self.backup_dir = self.base_dir / "ui_migration_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Template mappings
        self.base_template_mappings = {
            'base.html': 'unified_base.html',
            'enhanced_base_template.html': 'unified_base.html',
            'enhanced_base_demo.html': 'unified_base.html'
        }
        
        # Block mappings for template migration
        self.block_mappings = {
            'dashboard_content': 'content',
            'extra_styles': 'extra_css',
            'header_actions': 'page_actions'
        }
        
        self.migrated_files = []
        self.errors = []

    def create_backup(self):
        """Create backup of existing templates"""
        print(f"Creating backup at: {self.backup_dir}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup main templates
        if self.templates_dir.exists():
            shutil.copytree(self.templates_dir, self.backup_dir / "templates")
        
        # Backup module templates
        for module_path in self.modules_dir.glob("*/templates"):
            if module_path.is_dir():
                module_name = module_path.parent.name
                shutil.copytree(module_path, self.backup_dir / "modules" / module_name / "templates")

    def find_all_templates(self):
        """Find all HTML templates in the project"""
        templates = []
        
        # Main templates
        for template in self.templates_dir.glob("**/*.html"):
            if template.is_file():
                templates.append(template)
        
        # Module templates
        for template in self.modules_dir.glob("**/templates/**/*.html"):
            if template.is_file():
                templates.append(template)
        
        return templates

    def migrate_template_extends(self, content):
        """Migrate template extends statements"""
        for old_base, new_base in self.base_template_mappings.items():
            # Match extends statements
            pattern = rf'{{% extends ["\']({re.escape(old_base)})["\'] %}}'
            replacement = f'{{% extends "{new_base}" %}}'
            content = re.sub(pattern, replacement, content)
        
        return content

    def migrate_template_blocks(self, content):
        """Migrate template block names"""
        for old_block, new_block in self.block_mappings.items():
            # Match block definitions
            pattern = rf'{{% block {old_block} %}}'
            replacement = f'{{% block {new_block} %}}'
            content = re.sub(pattern, replacement, content)
            
            # Match endblock statements
            pattern = rf'{{% endblock {old_block} %}}'
            replacement = f'{{% endblock {new_block} %}}'
            content = re.sub(pattern, replacement, content)
        
        return content

    def add_component_imports(self, content):
        """Add component imports to templates that need them"""
        if "{% extends" in content and "{% from 'components/nvc_components.html'" not in content:
            # Find the position after extends statement
            extends_match = re.search(r'{% extends.*?%}', content)
            if extends_match:
                insert_pos = extends_match.end()
                import_statement = '\n{% from "components/nvc_components.html" import metric_card, action_card, account_card, transaction_row, form_input, form_select, notification_banner, progress_bar, stats_grid, loading_spinner, empty_state %}\n'
                content = content[:insert_pos] + import_statement + content[insert_pos:]
        
        return content

    def modernize_css_classes(self, content):
        """Replace old CSS classes with new unified classes"""
        class_mappings = {
            # Button classes
            'btn-primary': 'nvc-btn nvc-btn-primary',
            'btn-secondary': 'nvc-btn nvc-btn-secondary',
            'btn-outline': 'nvc-btn nvc-btn-outline',
            'btn-success': 'nvc-btn nvc-btn-success',
            'btn-warning': 'nvc-btn nvc-btn-warning',
            'btn-danger': 'nvc-btn nvc-btn-danger',
            
            # Card classes
            'card': 'nvc-card',
            'card-header': 'nvc-card-header',
            'card-body': 'nvc-card-body',
            'card-footer': 'nvc-card-footer',
            
            # Enterprise classes (from enhanced templates)
            'enterprise-btn enterprise-btn-primary': 'nvc-btn nvc-btn-primary',
            'enterprise-btn enterprise-btn-secondary': 'nvc-btn nvc-btn-secondary',
            'enterprise-btn enterprise-btn-outline': 'nvc-btn nvc-btn-outline',
            'enterprise-card': 'nvc-card',
            'enterprise-metric-card': 'nvc-metric-card',
            'banking-card': 'nvc-card',
            'banking-action-card': 'nvc-action-card',
            
            # Form classes
            'form-control': 'nvc-form-input',
            'form-select': 'nvc-form-select',
            'form-label': 'nvc-form-label',
            
            # Alert classes
            'alert': 'nvc-alert',
            'alert-success': 'nvc-alert-success',
            'alert-warning': 'nvc-alert-warning',
            'alert-danger': 'nvc-alert-danger',
            'alert-info': 'nvc-alert-info',
        }
        
        for old_class, new_class in class_mappings.items():
            # Replace class attributes
            content = re.sub(
                rf'class="([^"]*){re.escape(old_class)}([^"]*)"',
                rf'class="\1{new_class}\2"',
                content
            )
        
        return content

    def update_template_structure(self, content):
        """Update template structure to match unified base"""
        # Add page_actions block if header_actions exist
        if '{% block header_actions %}' in content:
            content = content.replace(
                '{% block header_actions %}',
                '{% block page_actions %}'
            )
            content = content.replace(
                '{% endblock header_actions %}',
                '{% endblock page_actions %}'
            )
        
        # Wrap content in proper structure if needed
        if '{% block content %}' in content and 'nvc-page-content' not in content:
            # Find content block and wrap it
            content_pattern = r'({% block content %})(.*?)({% endblock %})'
            def wrap_content(match):
                block_start = match.group(1)
                block_content = match.group(2)
                block_end = match.group(3)
                
                wrapped_content = f"""
<div class="nvc-page-content">
    {block_content.strip()}
</div>
"""
                return block_start + wrapped_content + block_end
            
            content = re.sub(content_pattern, wrap_content, content, flags=re.DOTALL)
        
        return content

    def migrate_template(self, template_path):
        """Migrate a single template file"""
        try:
            print(f"Migrating: {template_path}")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply migrations
            content = self.migrate_template_extends(content)
            content = self.migrate_template_blocks(content)
            content = self.add_component_imports(content)
            content = self.modernize_css_classes(content)
            content = self.update_template_structure(content)
            
            # Only write if content changed
            if content != original_content:
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.migrated_files.append(str(template_path))
                print(f"  ✓ Migrated successfully")
            else:
                print(f"  - No changes needed")
                
        except Exception as e:
            error_msg = f"Error migrating {template_path}: {str(e)}"
            self.errors.append(error_msg)
            print(f"  ✗ {error_msg}")

    def create_example_templates(self):
        """Create example templates showing the new unified system"""
        examples_dir = self.templates_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        # Example dashboard template
        dashboard_example = '''{% extends "unified_base.html" %}
{% from "components/nvc_components.html" import metric_card, action_card, account_card, stats_grid %}

{% block title %}Dashboard Example - NVC Banking Platform{% endblock %}
{% block page_title %}Dashboard Overview{% endblock %}
{% block page_description %}Comprehensive view of your banking operations{% endblock %}

{% block page_actions %}
<button class="nvc-btn nvc-btn-outline">
    <i class="fas fa-download"></i>
    <span class="nvc-btn-text">Export</span>
</button>
<button class="nvc-btn nvc-btn-primary">
    <i class="fas fa-plus"></i>
    <span class="nvc-btn-text">New Transaction</span>
</button>
{% endblock %}

{% block content %}
<div class="nvc-page-content">
    <!-- Key Metrics -->
    <div class="row g-4 mb-4">
        <div class="col-lg-3 col-md-6">
            {{ metric_card("Total Balance", "$125,430.50", "fas fa-wallet", "+5.2%", "positive") }}
        </div>
        <div class="col-lg-3 col-md-6">
            {{ metric_card("Monthly Income", "$8,250.00", "fas fa-arrow-up", "+12.3%", "positive") }}
        </div>
        <div class="col-lg-3 col-md-6">
            {{ metric_card("Monthly Expenses", "$3,180.75", "fas fa-arrow-down", "-2.1%", "positive") }}
        </div>
        <div class="col-lg-3 col-md-6">
            {{ metric_card("Savings Rate", "62.5%", "fas fa-piggy-bank", "+1.8%", "positive") }}
        </div>
    </div>

    <!-- Quick Actions -->
    <div class="row g-3 mb-4">
        <div class="col-lg-4 col-md-6">
            {{ action_card("Transfer Money", "Send money between accounts", "fas fa-exchange-alt", "/banking/transfer") }}
        </div>
        <div class="col-lg-4 col-md-6">
            {{ action_card("Pay Bills", "Manage recurring payments", "fas fa-file-invoice-dollar", "/banking/bills") }}
        </div>
        <div class="col-lg-4 col-md-6">
            {{ action_card("View Statements", "Download account statements", "fas fa-file-alt", "/banking/statements") }}
        </div>
    </div>

    <!-- Account Overview -->
    <div class="row g-4">
        <div class="col-lg-4 col-md-6">
            {{ account_card("Checking Account", "****1234", "$45,230.50", "fas fa-university", "active") }}
        </div>
        <div class="col-lg-4 col-md-6">
            {{ account_card("Savings Account", "****5678", "$80,200.00", "fas fa-piggy-bank", "active") }}
        </div>
        <div class="col-lg-4 col-md-6">
            {{ account_card("Investment Account", "****9012", "$125,430.75", "fas fa-chart-line", "active") }}
        </div>
    </div>
</div>
{% endblock %}'''

        with open(examples_dir / "dashboard_example.html", 'w') as f:
            f.write(dashboard_example)

        # Example form template
        form_example = '''{% extends "unified_base.html" %}
{% from "components/nvc_components.html" import form_input, form_select, notification_banner %}

{% block title %}Form Example - NVC Banking Platform{% endblock %}
{% block page_title %}Account Application{% endblock %}
{% block page_description %}Apply for a new banking account{% endblock %}

{% block content %}
<div class="nvc-page-content">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="nvc-card">
                <div class="nvc-card-header">
                    <h3 class="nvc-card-title">New Account Application</h3>
                </div>
                <div class="nvc-card-body">
                    {{ notification_banner("Please fill out all required fields to complete your application.", "info", True, "fas fa-info-circle") }}
                    
                    <form method="POST">
                        <div class="row">
                            <div class="col-md-6">
                                {{ form_input("First Name", "first_name", "text", "Enter your first name", "fas fa-user", True) }}
                            </div>
                            <div class="col-md-6">
                                {{ form_input("Last Name", "last_name", "text", "Enter your last name", "fas fa-user", True) }}
                            </div>
                        </div>
                        
                        {{ form_input("Email Address", "email", "email", "Enter your email address", "fas fa-envelope", True) }}
                        
                        {{ form_input("Phone Number", "phone", "tel", "Enter your phone number", "fas fa-phone", True) }}
                        
                        {{ form_select("Account Type", "account_type", [("checking", "Checking Account"), ("savings", "Savings Account"), ("business", "Business Account")], "fas fa-university", True) }}
                        
                        {{ form_input("Initial Deposit", "initial_deposit", "number", "Minimum $100", "fas fa-dollar-sign", True) }}
                        
                        <div class="d-flex gap-3 mt-4">
                            <button type="button" class="nvc-btn nvc-btn-outline">
                                <i class="fas fa-arrow-left"></i>
                                Back
                            </button>
                            <button type="submit" class="nvc-btn nvc-btn-primary">
                                <i class="fas fa-check"></i>
                                Submit Application
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

        with open(examples_dir / "form_example.html", 'w') as f:
            f.write(form_example)

        print(f"Created example templates in: {examples_dir}")

    def generate_migration_report(self):
        """Generate a detailed migration report"""
        report_path = self.base_dir / "ui_migration_report.md"
        
        report_content = f"""# NVC Banking Platform - UI Standardization Migration Report

**Migration Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Backup Location:** {self.backup_dir}

## Summary

- **Total Files Migrated:** {len(self.migrated_files)}
- **Errors Encountered:** {len(self.errors)}

## Files Successfully Migrated

"""
        
        for file_path in self.migrated_files:
            report_content += f"- {file_path}\n"
        
        if self.errors:
            report_content += "\n## Errors Encountered\n\n"
            for error in self.errors:
                report_content += f"- {error}\n"
        
        report_content += f"""
## Migration Changes Applied

### 1. Base Template Updates
- Migrated from multiple base templates to unified `unified_base.html`
- Updated template inheritance structure

### 2. Component System Integration
- Added component imports to templates
- Standardized UI components across all modules

### 3. CSS Class Modernization
- Replaced old Bootstrap classes with NVC unified classes
- Updated enterprise and banking-specific classes

### 4. Block Structure Updates
- Standardized template block names
- Improved content organization

## Next Steps

1. **Test All Migrated Templates:** Verify that all pages render correctly
2. **Update Custom Styles:** Review and update any custom CSS that may conflict
3. **Component Usage:** Consider replacing hardcoded HTML with component macros
4. **Documentation:** Update development documentation with new standards

## Rollback Instructions

If you need to rollback the migration:

```bash
# Remove current templates
rm -rf nvcfund-backend/templates
rm -rf nvcfund-backend/modules/*/templates

# Restore from backup
cp -r {self.backup_dir}/templates nvcfund-backend/
cp -r {self.backup_dir}/modules/* nvcfund-backend/modules/
```

## New Unified System Features

### Unified Base Template
- Consistent navigation and layout
- Professional banking theme
- Responsive design
- Accessibility improvements

### Component Library
- Reusable UI components
- Consistent styling
- Easy maintenance
- Better user experience

### Design System
- Standardized colors and typography
- Consistent spacing and sizing
- Professional appearance
- Brand consistency
"""
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        print(f"Migration report generated: {report_path}")

    def run_migration(self):
        """Run the complete migration process"""
        print("🏦 NVC Banking Platform - UI Standardization Migration")
        print("=" * 60)
        
        # Create backup
        self.create_backup()
        
        # Find all templates
        templates = self.find_all_templates()
        print(f"Found {len(templates)} templates to migrate")
        
        # Migrate each template
        for template in templates:
            self.migrate_template(template)
        
        # Create example templates
        self.create_example_templates()
        
        # Generate report
        self.generate_migration_report()
        
        print("\n" + "=" * 60)
        print("Migration Complete!")
        print(f"✓ {len(self.migrated_files)} files migrated successfully")
        if self.errors:
            print(f"⚠ {len(self.errors)} errors encountered")
        print(f"📁 Backup created at: {self.backup_dir}")
        print(f"📊 Report generated: ui_migration_report.md")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = "/Users/petersumanu/Documents/GitHub/nvcfund-2.0.0"
    
    migrator = UIStandardizationMigrator(base_dir)
    migrator.run_migration()
#!/usr/bin/env python3
"""
Route Connector for NVC Banking Platform
Automatically adds route connections for orphaned templates
"""

import os
import re
from pathlib import Path

# High-priority template to route mappings
TEMPLATE_ROUTE_MAPPINGS = {
    # Analytics Module
    'analytics/performance_metrics.html': {
        'module': 'analytics',
        'route_name': 'performance_metrics',
        'url_rule': '/performance',
        'function_name': 'performance_metrics',
        'description': 'Performance metrics analytics'
    },
    'analytics/user_analytics.html': {
        'module': 'analytics', 
        'route_name': 'user_analytics',
        'url_rule': '/user-analytics',
        'function_name': 'user_analytics',
        'description': 'User analytics dashboard'
    },
    
    # Security Center Module
    'security_center/waf_management.html': {
        'module': 'security_center',
        'route_name': 'waf_management',
        'url_rule': '/waf',
        'function_name': 'waf_management',
        'description': 'WAF management dashboard'
    },
    'security_center/ngfw_management.html': {
        'module': 'security_center',
        'route_name': 'ngfw_management', 
        'url_rule': '/ngfw',
        'function_name': 'ngfw_management',
        'description': 'Next-Gen Firewall management'
    },
    'security_center/xdr_dashboard.html': {
        'module': 'security_center',
        'route_name': 'xdr_dashboard',
        'url_rule': '/xdr',
        'function_name': 'xdr_dashboard', 
        'description': 'XDR security dashboard'
    },
    'security_center/fraud_detection_aml.html': {
        'module': 'security_center',
        'route_name': 'fraud_detection',
        'url_rule': '/fraud-detection',
        'function_name': 'fraud_detection',
        'description': 'Fraud detection and AML'
    },
    'security_center/ip_management.html': {
        'module': 'security_center',
        'route_name': 'ip_management',
        'url_rule': '/ip-management', 
        'function_name': 'ip_management',
        'description': 'IP address management'
    },
    'security_center/security_investigation.html': {
        'module': 'security_center',
        'route_name': 'security_investigation',
        'url_rule': '/investigation',
        'function_name': 'security_investigation',
        'description': 'Security investigation dashboard'
    },
    
    # System Management Module
    'system_management/dashboard.html': {
        'module': 'system_management',
        'route_name': 'system_dashboard',
        'url_rule': '/dashboard', 
        'function_name': 'system_dashboard',
        'description': 'System management dashboard'
    },
    'system_management/system_health.html': {
        'module': 'system_management',
        'route_name': 'system_health',
        'url_rule': '/health',
        'function_name': 'system_health',
        'description': 'System health monitoring'
    },
    'system_management/performance_monitoring.html': {
        'module': 'system_management',
        'route_name': 'performance_monitoring',
        'url_rule': '/performance',
        'function_name': 'performance_monitoring',
        'description': 'Performance monitoring dashboard'
    },
    
    # MFA Module
    'mfa/setup_totp.html': {
        'module': 'mfa',
        'route_name': 'setup_totp',
        'url_rule': '/setup-totp',
        'function_name': 'setup_totp',
        'description': 'TOTP setup interface'
    },
    'mfa/settings.html': {
        'module': 'mfa',
        'route_name': 'mfa_settings',
        'url_rule': '/settings',
        'function_name': 'mfa_settings', 
        'description': 'MFA settings management'
    },
    'mfa/activity_log.html': {
        'module': 'mfa',
        'route_name': 'activity_log',
        'url_rule': '/activity',
        'function_name': 'activity_log',
        'description': 'MFA activity log'
    }
}

def find_route_insertion_point(routes_file_content):
    """Find the best insertion point for new routes"""
    lines = routes_file_content.split('\n')
    
    # Look for the last route definition before health check or end of file
    insertion_line = -1
    for i, line in enumerate(lines):
        if '@' in line and '_bp.route(' in line:
            insertion_line = i
        elif 'health_check' in line and 'def' in line:
            break
    
    return insertion_line

def generate_route_code(template_info):
    """Generate Flask route code for a template"""
    return f"""
@{template_info['module']}_bp.route('{template_info['url_rule']}')
@login_required
def {template_info['function_name']}():
    \"\"\"{template_info['description']}\"\"\"
    try:
        return render_template('{template_info['route_name']}.html',
                             user=current_user,
                             page_title='{template_info['description']}')
    except Exception as e:
        error_service.log_error("{template_info['function_name'].upper()}_ERROR", str(e), {{"user_id": current_user.id}})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('{template_info['module']}.main_dashboard'))"""

def add_route_to_module(module_name, template_path, template_info):
    """Add route to specific module"""
    routes_file = f"nvcfund-backend/modules/{module_name}/routes.py"
    
    if not os.path.exists(routes_file):
        print(f"❌ Routes file not found: {routes_file}")
        return False
    
    try:
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if route already exists
        if template_info['function_name'] in content:
            print(f"⚠️  Route {template_info['function_name']} already exists in {module_name}")
            return False
        
        # Find insertion point
        insertion_point = find_route_insertion_point(content)
        
        if insertion_point == -1:
            print(f"❌ Could not find insertion point in {routes_file}")
            return False
        
        # Generate new route code
        route_code = generate_route_code(template_info)
        
        # Insert route code
        lines = content.split('\n')
        lines.insert(insertion_point + 1, route_code)
        
        # Write back to file
        with open(routes_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Added route {template_info['url_rule']} to {module_name} module")
        return True
        
    except Exception as e:
        print(f"❌ Error adding route to {module_name}: {e}")
        return False

def connect_orphaned_templates():
    """Main function to connect orphaned templates"""
    print("🔗 Connecting orphaned templates to routes...")
    print("=" * 60)
    
    connected_count = 0
    failed_count = 0
    
    for template_path, template_info in TEMPLATE_ROUTE_MAPPINGS.items():
        module_name = template_info['module']
        
        print(f"\n📝 Processing: {template_path}")
        print(f"   Module: {module_name}")
        print(f"   Route: {template_info['url_rule']}")
        
        success = add_route_to_module(module_name, template_path, template_info)
        
        if success:
            connected_count += 1
        else:
            failed_count += 1
    
    print(f"\n📊 Route Connection Summary:")
    print("=" * 60)
    print(f"✅ Successfully connected: {connected_count} templates")
    print(f"❌ Failed connections: {failed_count} templates")
    print(f"📈 Total processed: {len(TEMPLATE_ROUTE_MAPPINGS)} templates")
    
    if connected_count > 0:
        print(f"\n🎉 Route connections added successfully!")
        print(f"   Run the orphaned template checker again to verify results")
    
    return connected_count

if __name__ == "__main__":
    connected = connect_orphaned_templates()
    
    if connected > 0:
        print(f"\n⚡ NEXT STEPS:")
        print(f"   1. Restart the application to load new routes")
        print(f"   2. Run orphaned template checker to verify improvement")
        print(f"   3. Test new routes in the application")
    else:
        print(f"\n⚠️  No new routes were added. Check existing implementations.")
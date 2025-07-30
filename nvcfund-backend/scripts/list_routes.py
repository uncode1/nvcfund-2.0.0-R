#!/usr/bin/env python3
"""
List all available Flask routes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set minimal environment for testing
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
os.environ['DATA_ENCRYPTION_KEY'] = 'test-key-for-route-listing'
os.environ['SESSION_SECRET'] = 'test-session-secret'

from app_factory import create_app

def list_routes():
    """List all available routes"""
    
    app = create_app('development')
    
    with app.app_context():
        print("🔍 Available Flask Routes:")
        print("=" * 80)
        
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint:
                routes.append((rule.endpoint, rule.rule, list(rule.methods)))
        
        # Sort routes by endpoint
        routes.sort(key=lambda x: x[0])
        
        # Group by module
        current_module = None
        for endpoint, rule, methods in routes:
            module = endpoint.split('.')[0] if '.' in endpoint else 'main'
            
            if module != current_module:
                print(f"\n📁 {module.upper()} MODULE:")
                print("-" * 40)
                current_module = module
            
            methods_str = ', '.join(m for m in methods if m not in ['HEAD', 'OPTIONS'])
            print(f"   {endpoint:<40} {rule:<30} [{methods_str}]")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total routes: {len(routes)}")
        
        # Check specific routes we're interested in
        print(f"\n🔍 CHECKING NAVIGATION ROUTES:")
        nav_routes = [
            'user_management.profile_management',
            'user_management.user_dashboard', 
            'user_management.user_settings',
            'admin_management.admin_dashboard',
            'treasury.main_dashboard',
            'compliance.compliance_dashboard',
            'security_center.security_dashboard_new',
            'services.support_dashboard'
        ]
        
        available_endpoints = [route[0] for route in routes]
        
        for route in nav_routes:
            status = "✅ EXISTS" if route in available_endpoints else "❌ MISSING"
            print(f"   {route:<40} {status}")

if __name__ == '__main__':
    list_routes()

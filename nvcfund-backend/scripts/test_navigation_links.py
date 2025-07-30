#!/usr/bin/env python3
"""
Navigation Links Testing Script
Tests all navigation links to ensure they resolve correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_navigation_links():
    """Test all navigation links used in templates"""

    # Set minimal environment for testing
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    os.environ['DATA_ENCRYPTION_KEY'] = 'test-key-for-navigation-testing'
    os.environ['SESSION_SECRET'] = 'test-session-secret'

    from app_factory import create_app
    from flask import url_for

    app = create_app('development')
    
    with app.app_context():
        print("🔍 Testing Navigation Links...")
        print("=" * 50)
        
        # Test main navigation links
        navigation_links = [
            # Public routes
            ('public.index', 'Public Home'),
            ('public.about', 'About Page'),
            ('public.contact', 'Contact Page'),
            ('public.api_documentation', 'API Documentation'),
            
            # Auth routes
            ('auth.login', 'Login Page'),
            ('auth.register', 'Register Page'),
            ('auth.logout', 'Logout'),
            ('auth.forgot_password', 'Forgot Password'),
            
            # Dashboard routes
            ('dashboard.main', 'Dashboard Main'),
            ('dashboard.main_dashboard', 'Main Dashboard'),
            
            # User management routes
            ('user_management.profile', 'User Profile'),
            ('user_management.user_settings', 'User Settings'),
            
            # Security center routes
            ('security_center.security_dashboard_new', 'Security Center'),
            
            # Services routes
            ('services.support_dashboard', 'Support Dashboard'),
        ]
        
        working_links = []
        broken_links = []
        
        for route, description in navigation_links:
            try:
                url = url_for(route)
                working_links.append((route, description, url))
                print(f"✅ {description}: {route} -> {url}")
            except Exception as e:
                broken_links.append((route, description, str(e)))
                print(f"❌ {description}: {route} -> ERROR: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 SUMMARY:")
        print(f"✅ Working Links: {len(working_links)}")
        print(f"❌ Broken Links: {len(broken_links)}")
        
        if broken_links:
            print("\n🔧 BROKEN LINKS TO FIX:")
            for route, description, error in broken_links:
                print(f"   - {description} ({route}): {error}")
                
        print("\n💡 RECOMMENDATIONS:")
        if broken_links:
            print("   1. Check if the blueprint is properly registered")
            print("   2. Verify the route function exists in the module")
            print("   3. Ensure the module is imported correctly")
            print("   4. Consider adding fallback routes or error handling")
        else:
            print("   🎉 All navigation links are working correctly!")

if __name__ == '__main__':
    test_navigation_links()

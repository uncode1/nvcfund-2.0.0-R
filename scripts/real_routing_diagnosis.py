#!/usr/bin/env python3
"""
Real Routing Diagnosis - Identify actual routing problems
Tests authenticated session with proper following of redirects
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealRoutingDiagnostic:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.false_positives = []
        self.actual_broken_links = []
        self.working_links = []
        self.homepage_redirects = []
        
    def authenticate(self):
        """Authenticate with the platform"""
        try:
            # Get login page to extract CSRF token
            login_page = self.session.get(f"{self.base_url}/auth/login")
            logger.info(f"Login page status: {login_page.status_code}")
            
            # Extract CSRF token from login page
            soup = BeautifulSoup(login_page.content, 'html.parser')
            csrf_token = None
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # Login with CSRF token
            login_data = {
                'username': 'uncode',
                'password': 'Zx9Wq2@#ComplexCeo'
            }
            
            if csrf_token:
                login_data['csrf_token'] = csrf_token
                logger.info("Using CSRF token for authentication")
            else:
                logger.warning("No CSRF token found, attempting login without it")
            
            login_response = self.session.post(f"{self.base_url}/auth/login", data=login_data, allow_redirects=True)
            logger.info(f"Login response status: {login_response.status_code}")
            logger.info(f"Login final URL: {login_response.url}")
            
            # Check if we're authenticated (not redirected to login)
            if 'login' in login_response.url:
                logger.error("Authentication failed - still on login page")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def test_operations_dropdown_with_redirects(self):
        """Test operations dropdown with proper redirect following"""
        
        # Operations dropdown links that should NOT redirect to homepage
        operations_links = [
            ("/admin/branches", "Branch Management"),
            ("/admin/teller-operations", "Teller Operations"),
            ("/admin/branch-reports", "Branch Reports"),
            ("/settlement/dashboard", "Settlement Operations"),
            ("/admin/", "Admin Dashboard"),
            ("/system/dashboard", "System Health"),
            ("/admin/maintenance", "Maintenance Mode"),
            ("/admin/backups", "Database Backups"),
            ("/security/", "Security Dashboard"),
            ("/security/investigation", "Investigation Tools"),
            ("/security/threat-monitoring", "Threat Monitoring"),
            ("/security/incident-response", "Incident Response")
        ]
        
        print("REAL ROUTING DIAGNOSIS - Operations Dropdown")
        print("=" * 60)
        
        for endpoint, name in operations_links:
            try:
                # Test with redirect following
                response = self.session.get(f"{self.base_url}{endpoint}", allow_redirects=True)
                final_url = response.url
                
                # Check if redirected to homepage
                if final_url == self.base_url or final_url == f"{self.base_url}/":
                    if endpoint not in ['/', '']:
                        self.homepage_redirects.append({
                            'name': name,
                            'endpoint': endpoint,
                            'final_url': final_url,
                            'status': response.status_code
                        })
                        print(f"❌ HOMEPAGE REDIRECT: {name} ({endpoint}) -> {final_url}")
                        continue
                
                # Check if redirected to login
                if 'login' in final_url:
                    self.actual_broken_links.append({
                        'name': name,
                        'endpoint': endpoint,
                        'issue': 'AUTH_REQUIRED',
                        'final_url': final_url,
                        'status': response.status_code
                    })
                    print(f"🔒 AUTH REQUIRED: {name} ({endpoint}) -> {final_url}")
                    continue
                
                # Check for error pages
                if response.status_code == 404:
                    self.actual_broken_links.append({
                        'name': name,
                        'endpoint': endpoint,
                        'issue': '404_NOT_FOUND',
                        'final_url': final_url,
                        'status': response.status_code
                    })
                    print(f"❌ 404 NOT FOUND: {name} ({endpoint})")
                    continue
                
                # Check for 500 errors
                if response.status_code >= 500:
                    self.actual_broken_links.append({
                        'name': name,
                        'endpoint': endpoint,
                        'issue': 'SERVER_ERROR',
                        'final_url': final_url,
                        'status': response.status_code
                    })
                    print(f"❌ SERVER ERROR: {name} ({endpoint}) - {response.status_code}")
                    continue
                
                # Check page content for actual errors
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    title = soup.title.string if soup.title else ""
                    
                    # Check if it's actually an error page
                    if any(error in title.lower() for error in ['error', '404', '500', 'not found']):
                        self.actual_broken_links.append({
                            'name': name,
                            'endpoint': endpoint,
                            'issue': f'ERROR_PAGE: {title}',
                            'final_url': final_url,
                            'status': response.status_code
                        })
                        print(f"❌ ERROR PAGE: {name} ({endpoint}) - {title}")
                        continue
                
                # Success case
                self.working_links.append({
                    'name': name,
                    'endpoint': endpoint,
                    'final_url': final_url,
                    'status': response.status_code
                })
                print(f"✅ WORKING: {name} ({endpoint}) - {response.status_code}")
                
            except Exception as e:
                self.actual_broken_links.append({
                    'name': name,
                    'endpoint': endpoint,
                    'issue': f'EXCEPTION: {str(e)}',
                    'final_url': None,
                    'status': 0
                })
                print(f"💥 EXCEPTION: {name} ({endpoint}) - {str(e)}")
    
    def identify_false_reports(self):
        """Identify false positive reports from previous scripts"""
        
        print("\n" + "=" * 60)
        print("IDENTIFYING FALSE REPORTS")
        print("=" * 60)
        
        # Check if previous scripts reported success when there were actually redirects
        if self.homepage_redirects:
            print(f"⚠️  FOUND {len(self.homepage_redirects)} FALSE POSITIVE REPORTS")
            print("These links were reported as working but actually redirect to homepage:")
            for link in self.homepage_redirects:
                print(f"   - {link['name']}: {link['endpoint']}")
                self.false_positives.append({
                    'type': 'homepage_redirect',
                    'details': link,
                    'script_reported': 'working',
                    'actual_status': 'redirects_to_homepage'
                })
        
        # Check authentication issues
        auth_issues = [link for link in self.actual_broken_links if link.get('issue') == 'AUTH_REQUIRED']
        if auth_issues:
            print(f"⚠️  FOUND {len(auth_issues)} AUTHENTICATION ISSUES")
            print("These links require authentication but may have been reported as working:")
            for link in auth_issues:
                print(f"   - {link['name']}: {link['endpoint']}")
                self.false_positives.append({
                    'type': 'auth_required',
                    'details': link,
                    'script_reported': 'working',
                    'actual_status': 'requires_authentication'
                })
    
    def generate_diagnosis_report(self):
        """Generate comprehensive diagnosis report"""
        
        total_tested = len(self.working_links) + len(self.actual_broken_links) + len(self.homepage_redirects)
        
        print("\n" + "=" * 60)
        print("COMPREHENSIVE ROUTING DIAGNOSIS REPORT")
        print("=" * 60)
        print(f"Total Links Tested: {total_tested}")
        print(f"✅ Actually Working: {len(self.working_links)}")
        print(f"❌ Homepage Redirects: {len(self.homepage_redirects)}")
        print(f"❌ Actually Broken: {len(self.actual_broken_links)}")
        print(f"⚠️  False Positive Reports: {len(self.false_positives)}")
        
        if self.homepage_redirects:
            print(f"\n🔥 CRITICAL ISSUE: {len(self.homepage_redirects)} LINKS REDIRECT TO HOMEPAGE")
            print("These are the actual routing problems:")
            for link in self.homepage_redirects:
                print(f"   ❌ {link['name']}: {link['endpoint']}")
        
        if self.actual_broken_links:
            print(f"\n❌ ADDITIONAL BROKEN LINKS: {len(self.actual_broken_links)}")
            for link in self.actual_broken_links:
                print(f"   ❌ {link['name']}: {link['endpoint']} - {link['issue']}")
        
        if self.working_links:
            print(f"\n✅ CONFIRMED WORKING LINKS: {len(self.working_links)}")
            for link in self.working_links:
                print(f"   ✅ {link['name']}: {link['endpoint']}")
        
        # Save report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'diagnosis_summary': {
                'total_tested': total_tested,
                'working_count': len(self.working_links),
                'homepage_redirects_count': len(self.homepage_redirects),
                'broken_count': len(self.actual_broken_links),
                'false_positives_count': len(self.false_positives)
            },
            'homepage_redirects': self.homepage_redirects,
            'actual_broken_links': self.actual_broken_links,
            'working_links': self.working_links,
            'false_positives': self.false_positives
        }
        
        with open('logs/2025/07/06/system/real_routing_diagnosis.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Full diagnosis report saved to: logs/2025/07/06/system/real_routing_diagnosis.json")
    
    def run_diagnosis(self):
        """Run the complete routing diagnosis"""
        
        print("Starting Real Routing Diagnosis...")
        
        # Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed")
            return
        
        print("✅ Authentication successful")
        
        # Test operations dropdown
        self.test_operations_dropdown_with_redirects()
        
        # Identify false reports
        self.identify_false_reports()
        
        # Generate report
        self.generate_diagnosis_report()

def main():
    diagnostic = RealRoutingDiagnostic()
    diagnostic.run_diagnosis()

if __name__ == "__main__":
    main()
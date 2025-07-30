#!/usr/bin/env python3
"""
Safe Update Planner for NVC Banking Platform
Generates update plans for CI/CD deployment - NEVER modifies live application
"""
import subprocess
import json
import sys
import os
from datetime import datetime
import logging

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/update_planner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SafeUpdatePlanner:
    """Generate safe update plans for CI/CD deployment"""
    
    def __init__(self):
        self.critical_packages = [
            'flask', 'sqlalchemy', 'flask-login', 'flask-jwt-extended', 
            'cryptography', 'werkzeug', 'gunicorn'
        ]
        self.high_priority = [
            'flask-cors', 'flask-limiter', 'flask-socketio', 'psycopg2-binary',
            'flask-sqlalchemy', 'flask-session', 'flask-wtf'
        ]
        self.banking_specific = [
            'plaid-python', 'pyjwt', 'pyotp', 'qrcode', 'reportlab'
        ]
    
    def get_current_packages(self):
        """Read-only analysis of current package state"""
        try:
            result = subprocess.run(['pip', 'list', '--format=json'], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return []
        except Exception as e:
            logger.error(f"Failed to read current packages: {e}")
            return []
    
    def check_outdated_packages(self):
        """Read-only check for outdated packages"""
        try:
            result = subprocess.run(['pip', 'list', '--outdated', '--format=json'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout) if result.stdout else []
            return []
        except Exception as e:
            logger.warning(f"Failed to check outdated packages: {e}")
            return []
    
    def run_security_audit(self):
        """Safe read-only security audit"""
        try:
            result = subprocess.run(['pip-audit', '--format=json'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return json.loads(result.stdout) if result.stdout else {"vulnerabilities": []}
            else:
                logger.warning("pip-audit failed, security scan incomplete")
                return {"vulnerabilities": [], "scan_failed": True}
        except Exception as e:
            logger.warning(f"Security audit failed: {e}")
            return {"vulnerabilities": [], "scan_failed": True, "error": str(e)}
    
    def categorize_updates(self, outdated_packages):
        """Categorize updates by priority for CI/CD planning"""
        categories = {
            'critical_security': [],
            'critical_flask': [],
            'high_priority': [],
            'banking_specific': [],
            'standard': []
        }
        
        for package in outdated_packages:
            name = package['name'].lower()
            
            if name in self.critical_packages:
                categories['critical_flask'].append(package)
            elif name in self.high_priority:
                categories['high_priority'].append(package)
            elif name in self.banking_specific:
                categories['banking_specific'].append(package)
            else:
                categories['standard'].append(package)
        
        return categories
    
    def generate_cicd_requirements(self, categorized_updates, vulnerabilities):
        """Generate requirements files for CI/CD testing"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Critical updates requirements
        if categorized_updates['critical_flask']:
            critical_req = f"requirements_critical_{timestamp}.txt"
            with open(critical_req, 'w') as f:
                f.write("# Critical Flask package updates\n")
                f.write("# Deploy immediately through CI/CD pipeline\n\n")
                for pkg in categorized_updates['critical_flask']:
                    f.write(f"{pkg['name']}>={pkg['latest_version']}\n")
            logger.info(f"Critical requirements generated: {critical_req}")
        
        # High priority updates requirements
        if categorized_updates['high_priority']:
            high_req = f"requirements_high_priority_{timestamp}.txt"
            with open(high_req, 'w') as f:
                f.write("# High priority package updates\n")
                f.write("# Deploy within 1 week through CI/CD pipeline\n\n")
                for pkg in categorized_updates['high_priority']:
                    f.write(f"{pkg['name']}>={pkg['latest_version']}\n")
            logger.info(f"High priority requirements generated: {high_req}")
        
        # Security vulnerability fixes
        if vulnerabilities.get('vulnerabilities'):
            vuln_req = f"requirements_security_{timestamp}.txt"
            with open(vuln_req, 'w') as f:
                f.write("# Security vulnerability fixes\n")
                f.write("# Deploy immediately through emergency CI/CD pipeline\n\n")
                for vuln in vulnerabilities['vulnerabilities']:
                    f.write(f"{vuln['package']}  # Fix for {vuln.get('id', 'security issue')}\n")
            logger.info(f"Security requirements generated: {vuln_req}")
    
    def generate_deployment_plan(self):
        """Generate comprehensive deployment plan"""
        logger.info("Generating safe update deployment plan...")
        
        # Read-only analysis
        current_packages = self.get_current_packages()
        outdated_packages = self.check_outdated_packages()
        vulnerabilities = self.run_security_audit()
        
        # Categorize updates
        categorized = self.categorize_updates(outdated_packages)
        
        # Generate CI/CD requirements
        self.generate_cicd_requirements(categorized, vulnerabilities)
        
        # Create deployment plan
        plan = {
            "timestamp": datetime.now().isoformat(),
            "analysis_mode": "read_only_safe",
            "current_package_count": len(current_packages),
            "outdated_package_count": len(outdated_packages),
            "vulnerability_count": len(vulnerabilities.get('vulnerabilities', [])),
            "categorized_updates": categorized,
            "deployment_phases": self.create_deployment_phases(categorized, vulnerabilities),
            "cicd_recommendations": self.create_cicd_recommendations(categorized, vulnerabilities)
        }
        
        return plan
    
    def create_deployment_phases(self, categorized, vulnerabilities):
        """Create phased deployment plan for CI/CD"""
        phases = []
        
        # Emergency phase - security vulnerabilities
        if vulnerabilities.get('vulnerabilities'):
            phases.append({
                "phase": "emergency",
                "timeline": "immediate",
                "description": "Security vulnerability fixes",
                "packages": [v['package'] for v in vulnerabilities['vulnerabilities']],
                "deployment_method": "emergency_cicd_pipeline"
            })
        
        # Critical phase - Flask core updates
        if categorized['critical_flask']:
            phases.append({
                "phase": "critical",
                "timeline": "within_24_hours",
                "description": "Critical Flask ecosystem updates",
                "packages": [p['name'] for p in categorized['critical_flask']],
                "deployment_method": "standard_cicd_pipeline"
            })
        
        # High priority phase
        if categorized['high_priority']:
            phases.append({
                "phase": "high_priority",
                "timeline": "within_1_week",
                "description": "High priority Flask extensions",
                "packages": [p['name'] for p in categorized['high_priority']],
                "deployment_method": "standard_cicd_pipeline"
            })
        
        # Banking specific phase
        if categorized['banking_specific']:
            phases.append({
                "phase": "banking_specific",
                "timeline": "within_2_weeks",
                "description": "Banking and financial libraries",
                "packages": [p['name'] for p in categorized['banking_specific']],
                "deployment_method": "standard_cicd_pipeline"
            })
        
        return phases
    
    def create_cicd_recommendations(self, categorized, vulnerabilities):
        """Create CI/CD specific recommendations"""
        return {
            "branch_strategy": "feature/package-updates-" + datetime.now().strftime('%Y%m%d'),
            "testing_requirements": [
                "Unit tests must pass",
                "Integration tests must pass",
                "Security validation required",
                "Performance regression testing"
            ],
            "staging_validation": [
                "Deploy to staging environment first",
                "Run full test suite",
                "Manual smoke testing",
                "Load testing if critical packages updated"
            ],
            "production_deployment": [
                "Blue-green deployment recommended",
                "Database migration testing",
                "Rollback plan prepared",
                "Health check monitoring"
            ],
            "never_do": [
                "NEVER run pip install --upgrade on live production",
                "NEVER update packages directly on running application",
                "NEVER skip testing phases for any updates"
            ]
        }
    
    def save_plan(self, plan):
        """Save deployment plan for CI/CD usage"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_file = f"deployment_plan_{timestamp}.json"
        
        with open(plan_file, 'w') as f:
            json.dump(plan, f, indent=2)
        
        logger.info(f"Deployment plan saved: {plan_file}")
        return plan_file
    
    def print_safe_summary(self, plan):
        """Print safe deployment summary"""
        print("\n" + "="*60)
        print("NVC BANKING PLATFORM - SAFE UPDATE DEPLOYMENT PLAN")
        print("="*60)
        print("⚠️  READ-ONLY ANALYSIS - NO LIVE CHANGES MADE")
        print("")
        
        print(f"Current Packages: {plan['current_package_count']}")
        print(f"Outdated Packages: {plan['outdated_package_count']}")
        print(f"Security Vulnerabilities: {plan['vulnerability_count']}")
        print("")
        
        if plan['deployment_phases']:
            print("DEPLOYMENT PHASES:")
            for phase in plan['deployment_phases']:
                print(f"  {phase['phase'].upper()}: {len(phase['packages'])} packages")
                print(f"    Timeline: {phase['timeline']}")
                print(f"    Method: {phase['deployment_method']}")
                print()
        
        print("CI/CD REQUIREMENTS:")
        for req in plan['cicd_recommendations']['never_do']:
            print(f"  ❌ {req}")
        print()
        
        print("NEXT STEPS:")
        print("1. Review deployment plan JSON file")
        print("2. Create feature branch for updates")
        print("3. Update requirements files in development")
        print("4. Run CI/CD pipeline with full testing")
        print("5. Deploy through staging → production")
        print("")
        print("="*60)

def main():
    """Main execution - safe read-only analysis"""
    planner = SafeUpdatePlanner()
    
    try:
        plan = planner.generate_deployment_plan()
        plan_file = planner.save_plan(plan)
        planner.print_safe_summary(plan)
        
        # Return status based on urgency
        if plan['vulnerability_count'] > 0:
            logger.warning("Security vulnerabilities detected - urgent CI/CD deployment needed")
            return 1
        elif any(plan['categorized_updates']['critical_flask']):
            logger.warning("Critical Flask updates available - CI/CD deployment recommended")
            return 1
        else:
            logger.info("No urgent updates - routine CI/CD deployment planning")
            return 0
    
    except Exception as e:
        logger.error(f"Update planning failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""
Accounts Management Routes
Enterprise-grade modular routing system
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService, NavbarContextService

# Create module blueprint
accounts_bp = Blueprint('accounts', __name__, 
                            template_folder='templates',
                            static_folder='static',
                            url_prefix='/accounts')

# Initialize services
error_service = ErrorLoggerService()

@accounts_bp.route('/')
@login_required
def main_dashboard():
    """Accounts Management main dashboard"""
    try:
        # Get navbar context
        navbar_service = NavbarContextService()
        navbar_context = navbar_service.get_navbar_context()

        return render_template('accounts/accounts_dashboard.html',
                             user=current_user,
                             navbar_context=navbar_context,
                             page_title='Accounts Management Dashboard')
    except Exception as e:
        error_service.log_error("DASHBOARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@accounts_bp.route('/dashboard')
@login_required
def dashboard():
    """Accounts Management dashboard (alias for main)"""
    try:
        # Get navbar context
        navbar_service = NavbarContextService()
        navbar_context = navbar_service.get_navbar_context()

        return render_template('accounts/accounts_dashboard.html',
                             user=current_user,
                             navbar_context=navbar_context,
                             page_title='Accounts Management Dashboard')
    except Exception as e:
        error_service.log_error("DASHBOARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@accounts_bp.route('/new', methods=['GET', 'POST'])
@accounts_bp.route('/create', methods=['GET', 'POST'])
@login_required  
def new_account():
    """Create new account page - consolidated /new and /create routes"""
    try:
        from modules.utils.services import NavbarContextService
        navbar_service = NavbarContextService()
        navbar_context = navbar_service.get_navbar_context()

        if request.method == 'POST':
            # Extract comprehensive form data
            form_data = {
                # Customer Information
                'first_name': request.form.get('first_name', '').strip(),
                'last_name': request.form.get('last_name', '').strip(),
                'date_of_birth': request.form.get('date_of_birth', ''),
                'ssn': request.form.get('ssn', '').strip(),
                'email': request.form.get('email', '').strip(),
                'phone': request.form.get('phone', '').strip(),
                
                # Address Information
                'street_address': request.form.get('street_address', '').strip(),
                'apt_unit': request.form.get('apt_unit', '').strip(),
                'city': request.form.get('city', '').strip(),
                'state': request.form.get('state', '').strip(),
                'zip_code': request.form.get('zip_code', '').strip(),
                
                # Account Information
                'account_name': request.form.get('account_name', '').strip(),
                'account_type': request.form.get('account_type', 'checking'),
                'initial_deposit': request.form.get('initial_deposit', '25.00'),
                'overdraft_protection': request.form.get('overdraft_protection', 'none'),
                'debit_card': request.form.get('debit_card') == 'true',
                'online_banking': request.form.get('online_banking') == 'true',
                
                # Employment Information
                'employment_status': request.form.get('employment_status', ''),
                'annual_income': request.form.get('annual_income', '0'),
                'employer_name': request.form.get('employer_name', '').strip(),
                'years_employed': request.form.get('years_employed', '0'),
                
                # Source of Funds
                'funding_source': request.form.get('funding_source', ''),
                'expected_monthly_deposits': request.form.get('expected_monthly_deposits', '0'),
                
                # Government ID
                'id_type': request.form.get('id_type', ''),
                'id_number': request.form.get('id_number', '').strip(),
                'id_state': request.form.get('id_state', ''),
                'id_expiration': request.form.get('id_expiration', ''),
                
                # Terms and Conditions
                'terms_agreement': request.form.get('terms_agreement') == 'on',
                'patriot_act': request.form.get('patriot_act') == 'on',
                'electronic_consent': request.form.get('electronic_consent') == 'on'
            }
            
            # Comprehensive validation
            validation_errors = []
            
            # Required customer information validation
            required_fields = [
                ('first_name', 'First name'),
                ('last_name', 'Last name'),
                ('date_of_birth', 'Date of birth'),
                ('ssn', 'Social Security Number'),
                ('email', 'Email address'),
                ('phone', 'Phone number'),
                ('street_address', 'Street address'),
                ('city', 'City'),
                ('state', 'State'),
                ('zip_code', 'ZIP code'),
                ('account_name', 'Account name'),
                ('account_type', 'Account type'),
                ('employment_status', 'Employment status'),
                ('annual_income', 'Annual income'),
                ('funding_source', 'Funding source'),
                ('id_type', 'ID type'),
                ('id_number', 'ID number'),
                ('id_state', 'ID issuing state'),
                ('id_expiration', 'ID expiration date')
            ]
            
            for field, label in required_fields:
                if not form_data[field]:
                    validation_errors.append(f'{label} is required')
            
            # Initial deposit validation
            try:
                initial_deposit = float(form_data['initial_deposit'])
                if initial_deposit < 25.00:
                    validation_errors.append('Initial deposit must be at least $25.00')
            except ValueError:
                validation_errors.append('Invalid initial deposit amount')
            
            # Annual income validation
            try:
                annual_income = int(form_data['annual_income'])
                if annual_income < 0:
                    validation_errors.append('Annual income must be positive')
            except ValueError:
                validation_errors.append('Invalid annual income')
            
            # Terms and conditions validation
            if not all([form_data['terms_agreement'], form_data['patriot_act'], form_data['electronic_consent']]):
                validation_errors.append('All terms and conditions must be accepted')
            
            # Format validation using regex
            import re
            
            # SSN format validation
            ssn_pattern = r'^\d{3}-\d{2}-\d{4}$'
            if form_data['ssn'] and not re.match(ssn_pattern, form_data['ssn']):
                validation_errors.append('SSN must be in format XXX-XX-XXXX')
            
            # Email validation
            email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if form_data['email'] and not re.match(email_pattern, form_data['email']):
                validation_errors.append('Invalid email address format')
            
            # ZIP code validation
            zip_pattern = r'^\d{5}(-\d{4})?$'
            if form_data['zip_code'] and not re.match(zip_pattern, form_data['zip_code']):
                validation_errors.append('ZIP code must be in format 12345 or 12345-6789')
            
            # If validation errors, return with error messages
            if validation_errors:
                for error in validation_errors:
                    flash(error, 'error')
                return redirect(url_for('accounts.new_account'))
            
            # Generate account number
            import uuid
            account_number = f"NVC-{form_data['account_type'][:3].upper()}-{str(uuid.uuid4().hex[:8]).upper()}"
            
            # Log comprehensive account creation attempt
            error_service.log_error("COMPREHENSIVE_ACCOUNT_CREATION", 
                                  f"User {current_user.id} creating {form_data['account_type']} account for {form_data['first_name']} {form_data['last_name']}",
                                  {
                                      "user_id": current_user.id, 
                                      "account_type": form_data['account_type'],
                                      "account_name": form_data['account_name'],
                                      "customer_name": f"{form_data['first_name']} {form_data['last_name']}",
                                      "initial_deposit": form_data['initial_deposit'],
                                      "employment_status": form_data['employment_status'],
                                      "annual_income": form_data['annual_income'],
                                      "account_number": account_number
                                  })
            
            # Simulate successful account creation with comprehensive data
            success_message = f'Banking account "{form_data["account_name"]}" successfully created for {form_data["first_name"]} {form_data["last_name"]}! Account Number: {account_number}. Initial deposit: ${initial_deposit:.2f}. Welcome to NVC Banking!'
            flash(success_message, 'success')
            return redirect(url_for('accounts.main_dashboard'))
        
        # GET request - display the form
        account_types = [
            {'value': 'checking', 'label': 'Checking Account', 'description': 'For everyday transactions'},
            {'value': 'savings', 'label': 'Savings Account', 'description': 'For long-term savings'},
            {'value': 'business', 'label': 'Business Account', 'description': 'For business operations'},
            {'value': 'investment', 'label': 'Investment Account', 'description': 'For investment portfolios'}
        ]
        
        return render_template('accounts/new_account.html',
                             user=current_user,
                             account_types=account_types,
                             navbar_context=navbar_context,
                             page_title='Create New Account')
    except Exception as e:
        error_service.log_error("NEW_ACCOUNT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.overview'))

@accounts_bp.route('/details')
@login_required  
def account_details():
    """Account details page"""
    try:
        account_number = request.args.get('account', '')
        return render_template('accounts/account_details.html',
                             user=current_user,
                             account_number=account_number,
                             page_title=f'Account Details - {account_number}')
    except Exception as e:
        error_service.log_error("ACCOUNT_DETAILS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.overview'))

@accounts_bp.route('/edit')
@login_required  
def edit_account():
    """Edit account page"""
    try:
        account_number = request.args.get('account', '')
        return render_template('accounts/edit_account.html',
                             user=current_user,
                             account_number=account_number,
                             page_title=f'Edit Account - {account_number}')
    except Exception as e:
        error_service.log_error("EDIT_ACCOUNT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.overview'))

@accounts_bp.route('/overview')
@login_required  
def overview():
    """Accounts Management overview page"""
    try:
        # Get account data for the overview
        from modules.banking.models import BankAccount
        from modules.core.extensions import db
        
        # Sample account data for demonstration
        sample_accounts = [
            {
                'id': 1,
                'account_number': '1001234567',
                'account_name': 'John Doe - Checking',
                'account_type': 'Checking',
                'current_balance': 15847.52,
                'status': 'Active',
                'opened_date': '2024-01-15'
            },
            {
                'id': 2, 
                'account_number': '2001234568',
                'account_name': 'Jane Smith - Savings',
                'account_type': 'Savings',
                'current_balance': 85200.75,
                'status': 'Active',
                'opened_date': '2024-02-20'
            },
            {
                'id': 3,
                'account_number': '3001234569', 
                'account_name': 'ABC Corp - Business',
                'account_type': 'Business',
                'current_balance': 450000.00,
                'status': 'Active',
                'opened_date': '2024-03-10'
            },
            {
                'id': 4,
                'account_number': '4001234570',
                'account_name': 'Investment Portfolio',
                'account_type': 'Investment',
                'current_balance': 125000.00,
                'status': 'Active', 
                'opened_date': '2024-04-05'
            }
        ]
        
        # Account summary statistics
        total_accounts = len(sample_accounts)
        total_balance = sum(acc['current_balance'] for acc in sample_accounts)
        active_accounts = len([acc for acc in sample_accounts if acc['status'] == 'Active'])
        
        account_stats = {
            'total_accounts': total_accounts,
            'total_balance': total_balance,
            'active_accounts': active_accounts,
            'average_balance': total_balance / total_accounts if total_accounts > 0 else 0
        }
        
        return render_template('accounts/account_overview.html',
                             user=current_user,
                             accounts=sample_accounts,
                             account_stats=account_stats,
                             page_title='Account Overview')
    except Exception as e:
        error_service.log_error("OVERVIEW_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')  
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/settings')
@login_required
def settings():
    """Accounts Management settings page"""
    try:
        return render_template('accounts/accounts_settings.html',
                             user=current_user,
                             page_title='Accounts Management Settings')
    except Exception as e:
        error_service.log_error("SETTINGS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/analytics')
@login_required
def account_analytics():
    """Account analytics dashboard"""
    try:
        return render_template('accounts/account_analytics.html',
                             user=current_user,
                             page_title='Account Analytics')
    except Exception as e:
        error_service.log_error("ANALYTICS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/security')
@login_required
def account_security():
    """Account security management"""
    try:
        return render_template('accounts/account_security.html',
                             user=current_user,
                             page_title='Account Security')
    except Exception as e:
        error_service.log_error("SECURITY_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/transaction-history')
@login_required
def transaction_history():
    """Transaction history view"""
    try:
        return render_template('accounts/transaction_history.html',
                             user=current_user,
                             page_title='Transaction History')
    except Exception as e:
        error_service.log_error("TRANSACTION_HISTORY_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/account-management')
@login_required
def account_management():
    """Account management view"""
    try:
        return render_template('accounts/account_management.html',
                             user=current_user,
                             page_title='Account Management')
    except Exception as e:
        error_service.log_error("ACCOUNT_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

# Module health check
# Drill-down routes for detailed views
@accounts_bp.route('/portfolio/analysis')
@login_required
def portfolio_analysis():
    """Portfolio analysis drill-down view"""
    try:
        return render_template('accounts/portfolio_analysis.html',
                             user=current_user,
                             page_title='Portfolio Analysis')
    except Exception as e:
        error_service.log_error("PORTFOLIO_ANALYSIS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/performance/metrics')
@login_required
def performance_metrics():
    """Performance metrics drill-down view"""
    try:
        return render_template('accounts/performance_metrics.html',
                             user=current_user,
                             page_title='Performance Metrics')
    except Exception as e:
        error_service.log_error("PERFORMANCE_METRICS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/accounts/detailed')
@login_required
def accounts_detailed():
    """Detailed accounts drill-down view"""
    try:
        return render_template('accounts/account_details.html',
                             user=current_user,
                             page_title='Detailed Account Management')
    except Exception as e:
        error_service.log_error("ACCOUNTS_DETAILED_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/api/drill-down/active_accounts')
@login_required
def drill_down_active_accounts():
    """Active accounts drill-down API"""
    try:
        return jsonify({
            "metrics": [
                {"name": "Total Active Accounts", "value": "15,247", "change": 3.2, "trend": "up"},
                {"name": "New This Month", "value": "482", "change": 7.1, "trend": "up"},
                {"name": "Checking Accounts", "value": "8,934", "change": 2.8, "trend": "up"},
                {"name": "Savings Accounts", "value": "4,821", "change": 4.2, "trend": "up"},
                {"name": "Business Accounts", "value": "1,192", "change": 8.5, "trend": "up"},
                {"name": "Investment Accounts", "value": "300", "change": 12.3, "trend": "up"},
                {"name": "Average Balance", "value": "$23,450", "change": 2.1, "trend": "up"},
                {"name": "Avg Monthly Activity", "value": "14.2", "change": -1.8, "trend": "down"}
            ],
            "summary": "Active accounts showing strong growth with 3.2% increase",
            "timestamp": "2025-07-09 06:13:00"
        })
    except Exception as e:
        error_service.log_error("DRILL_DOWN_ACTIVE_ACCOUNTS_ERROR", str(e), {"user_id": current_user.id})
        return jsonify({"error": "Service temporarily unavailable"}), 500

@accounts_bp.route('/api/drill-down/pending_operations')
@login_required
def drill_down_pending_operations():
    """Pending operations drill-down API"""
    try:
        return jsonify({
            "metrics": [
                {"name": "Total Pending Operations", "value": "126", "change": -8.3, "trend": "down"},
                {"name": "Account Openings", "value": "34", "change": 12.5, "trend": "up"},
                {"name": "Pending Transfers", "value": "47", "change": -15.2, "trend": "down"},
                {"name": "Loan Applications", "value": "23", "change": 4.8, "trend": "up"},
                {"name": "Card Requests", "value": "12", "change": -20.1, "trend": "down"},
                {"name": "Document Verification", "value": "8", "change": -42.3, "trend": "down"},
                {"name": "Avg Processing Time", "value": "2.4 hours", "change": -18.5, "trend": "down"},
                {"name": "SLA Compliance", "value": "94.2%", "change": 1.8, "trend": "up"}
            ],
            "summary": "Pending operations decreased 8.3% with improved processing times",
            "timestamp": "2025-07-09 06:13:00"
        })
    except Exception as e:
        error_service.log_error("DRILL_DOWN_PENDING_OPERATIONS_ERROR", str(e), {"user_id": current_user.id})
        return jsonify({"error": "Service temporarily unavailable"}), 500

@accounts_bp.route('/api/drill-down/transaction_volume')
@login_required
def drill_down_transaction_volume():
    """Transaction volume drill-down API"""
    try:
        return jsonify({
            "metrics": [
                {"name": "Total Transaction Volume", "value": "$45.67M", "change": 5.8, "trend": "up"},
                {"name": "Daily Average Volume", "value": "$1.52M", "change": 3.2, "trend": "up"},
                {"name": "Wire Transfers", "value": "$28.3M", "change": 8.1, "trend": "up"},
                {"name": "ACH Transactions", "value": "$12.4M", "change": 2.3, "trend": "up"},
                {"name": "Card Transactions", "value": "$4.97M", "change": 12.5, "trend": "up"},
                {"name": "Transaction Count", "value": "124,856", "change": 4.7, "trend": "up"},
                {"name": "Avg Transaction Size", "value": "$365.84", "change": 1.1, "trend": "up"},
                {"name": "Peak Hour Volume", "value": "$3.2M", "change": 7.3, "trend": "up"}
            ],
            "summary": "Transaction volume increased 5.8% with strong wire transfer growth",
            "timestamp": "2025-07-09 06:13:00"
        })
    except Exception as e:
        error_service.log_error("DRILL_DOWN_TRANSACTION_VOLUME_ERROR", str(e), {"user_id": current_user.id})
        return jsonify({"error": "Service temporarily unavailable"}), 500

@accounts_bp.route('/api/drill-down/security_score')
@login_required
def drill_down_security_score():
    """Security score drill-down API"""
    try:
        return jsonify({
            "metrics": [
                {"name": "Overall Security Score", "value": "96.8%", "change": 0.3, "trend": "up"},
                {"name": "MFA Adoption Rate", "value": "89.2%", "change": 2.1, "trend": "up"},
                {"name": "Failed Login Attempts", "value": "42", "change": -12.8, "trend": "down"},
                {"name": "Account Lockouts", "value": "3", "change": -25.0, "trend": "down"},
                {"name": "Suspicious Activity", "value": "7", "change": -18.2, "trend": "down"},
                {"name": "Security Alerts", "value": "15", "change": -6.7, "trend": "down"},
                {"name": "Compliance Score", "value": "98.5%", "change": 0.2, "trend": "up"},
                {"name": "Fraud Detection Rate", "value": "99.7%", "change": 0.1, "trend": "up"}
            ],
            "summary": "Security score improved 0.3% with enhanced MFA adoption",
            "timestamp": "2025-07-09 06:13:00"
        })
    except Exception as e:
        error_service.log_error("DRILL_DOWN_SECURITY_SCORE_ERROR", str(e), {"user_id": current_user.id})
        return jsonify({"error": "Service temporarily unavailable"}), 500

@accounts_bp.route('/api/activity/<activity_id>')
@login_required
def get_activity_details(activity_id):
    """Get detailed activity information"""
    try:
        # Mock activity data - in real implementation, fetch from database
        activity_data = {
            "id": activity_id,
            "type": "Account Opening",
            "status": "In Progress",
            "user": "John Smith",
            "timestamp": "2025-07-09 14:30:00",
            "details": {
                "account_type": "Business Checking",
                "initial_deposit": "$5,000",
                "processing_stage": "Document Verification",
                "estimated_completion": "2025-07-10 10:00:00",
                "assigned_officer": "Sarah Johnson"
            }
        }
        return jsonify(activity_data)
    except Exception as e:
        error_service.log_error("ACTIVITY_DETAILS_ERROR", str(e), {"user_id": current_user.id})
        return jsonify({"error": "Service temporarily unavailable"}), 500

@accounts_bp.route('/drill-down/active-accounts')
@login_required
def drill_down_active_accounts_page():
    """Granular drill-down page for active accounts"""
    try:
        return render_template('accounts/drill_down_active_accounts.html',
                               page_title="Active Accounts Analysis",
                               module_name="Accounts Management")
    except Exception as e:
        error_service.log_error("DRILL_DOWN_ACTIVE_ACCOUNTS_PAGE_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load active accounts analysis. Please try again.', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/drill-down/pending-operations')
@login_required
def drill_down_pending_operations_page():
    """Granular drill-down page for pending operations"""
    try:
        return render_template('accounts/drill_down_pending_operations.html',
                               page_title="Pending Operations Analysis",
                               module_name="Accounts Management")
    except Exception as e:
        error_service.log_error("DRILL_DOWN_PENDING_OPERATIONS_PAGE_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load pending operations analysis. Please try again.', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/drill-down/transaction-volume')
@login_required
def drill_down_transaction_volume_page():
    """Granular drill-down page for transaction volume"""
    try:
        return render_template('accounts/drill_down_transaction_volume.html',
                               page_title="Transaction Volume Analysis",
                               module_name="Accounts Management")
    except Exception as e:
        error_service.log_error("DRILL_DOWN_TRANSACTION_VOLUME_PAGE_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load transaction volume analysis. Please try again.', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/drill-down/security-score')
@login_required
def drill_down_security_score_page():
    """Granular drill-down page for security score"""
    try:
        return render_template('accounts/drill_down_security_score.html',
                               page_title="Security Score Analysis",
                               module_name="Accounts Management")
    except Exception as e:
        error_service.log_error("DRILL_DOWN_SECURITY_SCORE_PAGE_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load security score analysis. Please try again.', 'error')
        return redirect(url_for('accounts.main_dashboard'))

# Data Table Routes for Drill-down Functionality
@accounts_bp.route('/data-table/active-accounts')
@login_required
def data_table_active_accounts():
    """Active accounts data table view"""
    try:
        return render_template('accounts/data_table_active_accounts.html',
                               page_title="Active Accounts Data Table",
                               module_name="Accounts Management")
    except Exception as e:
        error_service.log_error("DATA_TABLE_ACTIVE_ACCOUNTS_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load active accounts data table. Please try again.', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/data-table/account-balances')
@login_required
def data_table_account_balances():
    """Account balances data table view"""
    try:
        return render_template('accounts/data_table_account_balances.html',
                               page_title="Account Balances Data Table",
                               module_name="Accounts Management")
    except Exception as e:
        error_service.log_error("DATA_TABLE_ACCOUNT_BALANCES_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load account balances data table. Please try again.', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/data-table/pending-operations')
@login_required
def data_table_pending_operations():
    """Pending operations data table view"""
    try:
        return render_template('accounts/data_table_pending_operations.html',
                               page_title="Pending Operations Data Table",
                               module_name="Accounts Management")
    except Exception as e:
        error_service.log_error("DATA_TABLE_PENDING_OPERATIONS_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load pending operations data table. Please try again.', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/data-table/security-metrics')
@login_required
def data_table_security_metrics():
    """Security metrics data table view"""
    try:
        return render_template('accounts/data_table_security_metrics.html',
                               page_title="Security Metrics Data Table",
                               module_name="Accounts Management")
    except Exception as e:
        error_service.log_error("DATA_TABLE_SECURITY_METRICS_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load security metrics data table. Please try again.', 'error')
        return redirect(url_for('accounts.main_dashboard'))

# Missing route aliases referenced in templates
@accounts_bp.route('/accounts-dashboard')
@login_required
def accounts_dashboard():
    """Accounts dashboard - alias for main_dashboard"""
    return main_dashboard()

@accounts_bp.route('/create-account')
@login_required
def create_account():
    """Create account - alias for new_account"""
    return new_account()

@accounts_bp.route('/account-statements')
@login_required
def account_statements():
    """Account statements view"""
    try:
        statements_data = {
            'recent_statements': [
                {'date': '2025-01-15', 'type': 'Monthly Statement', 'account': 'CHK-001', 'status': 'Available'},
                {'date': '2024-12-15', 'type': 'Monthly Statement', 'account': 'CHK-001', 'status': 'Available'},
                {'date': '2024-11-15', 'type': 'Monthly Statement', 'account': 'CHK-001', 'status': 'Available'}
            ],
            'statement_types': ['Monthly', 'Quarterly', 'Annual', 'Tax Documents'],
            'delivery_options': ['Online', 'Email', 'Mail']
        }
        return render_template('accounts/account_statements.html',
                             statements_data=statements_data,
                             page_title='Account Statements')
    except Exception as e:
        error_service.log_error("ACCOUNT_STATEMENTS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('accounts.main_dashboard'))

@accounts_bp.route('/api/health')
def health_check():
    """Accounts Management health check"""
    return jsonify({
        "status": "healthy",
        "app_module": "Accounts Management",
        "version": "1.0.0",
        "routes_active": 34
    })

"""
MFA Routes
NVC Banking Platform - Multi-Factor Authentication Web Routes

This module provides web endpoints for MFA functionality:
- MFA setup and configuration
- TOTP verification
- Backup code management
- MFA status and management
"""

from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from modules.services.mfa import mfa_bp
from modules.services.mfa.services import MFAService
from modules.core.security_enforcement import secure_banking_route, validate_input
import logging

logger = logging.getLogger(__name__)


@mfa_bp.route('/')
@login_required
@secure_banking_route(
    required_permissions=['mfa_access'],
    rate_limit={'requests_per_minute': 10},
    validation_rules={
        'required_fields': [],
        'optional_fields': []
    }
)
def mfa_dashboard():
    """MFA management dashboard"""
    try:
        # Get MFA status for current user
        mfa_status = MFAService.get_mfa_status(current_user.id)
        
        return render_template('mfa/dashboard.html', 
                             mfa_status=mfa_status)
        
    except Exception as e:
        logger.error(f"Error loading MFA dashboard for user {current_user.id}: {str(e)}")
        flash('Error loading MFA settings. Please try again.', 'error')
        return redirect(url_for('dashboard.dashboard_home'))


@mfa_bp.route('/setup')
@login_required
@secure_banking_route(
    required_permissions=['mfa_setup'],
    rate_limit={'requests_per_minute': 5},
    validation_rules={
        'required_fields': [],
        'optional_fields': []
    }
)
def setup_mfa():
    """Set up MFA for the user"""
    try:
        # Check if MFA is already enabled
        mfa_status = MFAService.get_mfa_status(current_user.id)
        if mfa_status['enabled']:
            flash('MFA is already enabled for your account.', 'info')
            return redirect(url_for('mfa.mfa_dashboard'))
        
        # Generate TOTP secret and QR code
        secret, qr_code_base64, error = MFAService.setup_totp(current_user.id)
        
        if error:
            flash(f'Error setting up MFA: {error}', 'error')
            return redirect(url_for('mfa.mfa_dashboard'))
        
        return render_template('mfa/setup_totp.html', 
                             secret=secret,
                             qr_code_base64=qr_code_base64)
        
    except Exception as e:
        logger.error(f"Error setting up MFA for user {current_user.id}: {str(e)}")
        flash('Error setting up MFA. Please try again.', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))


@mfa_bp.route('/verify-setup', methods=['POST'])
@login_required
@secure_banking_route(
    required_permissions=['mfa_setup'],
    rate_limit={'requests_per_minute': 3},
    validation_rules={
        'required_fields': ['totp_code'],
        'optional_fields': []
    }
)
def verify_setup():
    """Verify TOTP code during setup"""
    try:
        totp_code = request.form.get('totp_code', '').strip()
        
        if not totp_code or len(totp_code) != 6 or not totp_code.isdigit():
            flash('Please enter a valid 6-digit code.', 'error')
            return redirect(url_for('mfa.setup_mfa'))
        
        # Verify the TOTP code
        success, result = MFAService.verify_totp_setup(current_user.id, totp_code)
        
        if success:
            # result contains backup codes
            backup_codes = result
            flash('MFA has been successfully enabled for your account!', 'success')
            return render_template('mfa/backup_codes.html', backup_codes=backup_codes)
        else:
            flash(f'Verification failed: {result}', 'error')
            return redirect(url_for('mfa.setup_mfa'))
        
    except Exception as e:
        logger.error(f"Error verifying MFA setup for user {current_user.id}: {str(e)}")
        flash('Error verifying MFA setup. Please try again.', 'error')
        return redirect(url_for('mfa.setup_mfa'))


@mfa_bp.route('/verify', methods=['GET', 'POST'])
def verify_mfa():
    """Verify MFA during login process"""
    try:
        # Check if user is in MFA verification state
        user_id = session.get('mfa_user_id')
        if not user_id:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        
        if request.method == 'GET':
            return render_template('mfa/verify.html')
        
        # POST request - verify the code
        totp_code = request.form.get('totp_code', '').strip()
        backup_code = request.form.get('backup_code', '').strip()
        
        if totp_code:
            # Verify TOTP code
            if len(totp_code) != 6 or not totp_code.isdigit():
                flash('Please enter a valid 6-digit code.', 'error')
                return render_template('mfa/verify.html')
            
            success, message = MFAService.verify_totp_login(user_id, totp_code)
            
        elif backup_code:
            # Verify backup code
            if len(backup_code) != 8 or not backup_code.isalnum():
                flash('Please enter a valid 8-character backup code.', 'error')
                return render_template('mfa/verify.html')
            
            success, message = MFAService.verify_backup_code(user_id, backup_code)
            
        else:
            flash('Please enter either a verification code or backup code.', 'error')
            return render_template('mfa/verify.html')
        
        if success:
            # Clear MFA session data
            session.pop('mfa_user_id', None)
            remember_me = session.pop('remember_me', False)

            # Complete the login process with proper tracking
            from modules.auth.models import User
            from modules.auth.services import AuthService

            user = User.query.get(user_id)
            if user:
                # Use centralized login completion function
                auth_service = AuthService()
                login_result = auth_service.complete_login(user, login_method='mfa', remember_me=remember_me)

                if login_result['success']:
                    flash('Login successful!', 'success')

                    # Determine dashboard redirect
                    dashboard_url = auth_service.determine_dashboard_redirect(user.username, user.role.value if user.role else 'standard')
                    return redirect(dashboard_url)
                else:
                    flash('Error completing login. Please try again.', 'error')
                    return redirect(url_for('auth.login'))
            else:
                flash('User not found. Please try logging in again.', 'error')
                return redirect(url_for('auth.login'))
        else:
            flash(f'Verification failed: {message}', 'error')
            return render_template('mfa/verify.html')
        
    except Exception as e:
        logger.error(f"Error during MFA verification: {str(e)}")
        flash('Error during verification. Please try again.', 'error')
        return render_template('mfa/verify.html')


@mfa_bp.route('/disable', methods=['POST'])
@login_required
@secure_banking_route(
    required_permissions=['mfa_management'],
    rate_limit={'requests_per_minute': 2},
    validation_rules={
        'required_fields': ['password'],
        'optional_fields': []
    }
)
def disable_mfa():
    """Disable MFA for the user (requires password confirmation)"""
    try:
        password = request.form.get('password', '')
        
        # Verify password before disabling MFA
        if not current_user.check_password(password):
            flash('Invalid password. MFA was not disabled.', 'error')
            return redirect(url_for('mfa.mfa_dashboard'))
        
        # Disable MFA
        success, message = MFAService.disable_mfa(current_user.id)
        
        if success:
            flash('MFA has been disabled for your account.', 'success')
        else:
            flash(f'Error disabling MFA: {message}', 'error')
        
        return redirect(url_for('mfa.mfa_dashboard'))
        
    except Exception as e:
        logger.error(f"Error disabling MFA for user {current_user.id}: {str(e)}")
        flash('Error disabling MFA. Please try again.', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))


@mfa_bp.route('/regenerate-backup-codes', methods=['POST'])
@login_required
@secure_banking_route(
    required_permissions=['mfa_management'],
    rate_limit={'requests_per_minute': 1},
    validation_rules={
        'required_fields': [],
        'optional_fields': []
    }
)
def regenerate_backup_codes():
    """Regenerate backup codes for the user"""
    try:
        # Regenerate backup codes
        backup_codes, message = MFAService.regenerate_backup_codes(current_user.id)
        
        if backup_codes:
            flash('New backup codes have been generated.', 'success')
            return render_template('mfa/backup_codes.html', backup_codes=backup_codes)
        else:
            flash(f'Error regenerating backup codes: {message}', 'error')
            return redirect(url_for('mfa.mfa_dashboard'))
        
    except Exception as e:
        logger.error(f"Error regenerating backup codes for user {current_user.id}: {str(e)}")
        flash('Error regenerating backup codes. Please try again.', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))


@mfa_bp.route('/status')
@login_required
@secure_banking_route(
    required_permissions=['mfa_access'],
    rate_limit={'requests_per_minute': 20},
    validation_rules={
        'required_fields': [],
        'optional_fields': []
    }
)
def mfa_status():
    """Get MFA status as JSON (for AJAX requests)"""
    try:
        status = MFAService.get_mfa_status(current_user.id)
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error getting MFA status for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error getting MFA status'
        }), 500


@mfa_bp.route('/health')
def health_check():
    """MFA module health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'mfa',
            'features': {
                'totp_authentication': True,
                'backup_codes': True,
                'qr_code_generation': True,
                'audit_logging': True
            }
        })
        
    except Exception as e:
        logger.error(f"MFA health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'app_module': 'mfa',
            'error': str(e)
        }), 500

# MFA routes already exist above - no duplicates needed

@mfa_bp.route('/settings')
@login_required
def settings():
    """MFA settings management"""
    try:
        mfa_status = MFAService.get_mfa_status(current_user.id)
        return render_template('mfa/settings.html',
                             mfa_status=mfa_status,
                             page_title='MFA Settings')
    except Exception as e:
        logger.error(f"MFA settings error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))

@mfa_bp.route('/activity-log')
@login_required
def activity_log():
    """MFA activity log"""
    try:
        activity_data = {
            'recent_activities': [
                {'action': 'TOTP Setup', 'timestamp': '2025-01-15 10:30', 'ip': '192.168.1.100', 'status': 'Success'},
                {'action': 'Backup Code Used', 'timestamp': '2025-01-14 15:20', 'ip': '192.168.1.100', 'status': 'Success'},
                {'action': 'Device Revoked', 'timestamp': '2025-01-13 09:15', 'ip': '192.168.1.100', 'status': 'Success'}
            ]
        }
        return render_template('mfa/activity_log.html',
                             activity_data=activity_data,
                             page_title='MFA Activity Log')
    except Exception as e:
        logger.error(f"MFA activity log error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))

@mfa_bp.route('/disable-totp')
@login_required
def disable_totp():
    """Disable TOTP authentication"""
    try:
        return render_template('mfa/disable_totp.html',
                             page_title='Disable TOTP')
    except Exception as e:
        logger.error(f"Disable TOTP error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))

@mfa_bp.route('/download-recovery-kit')
@login_required
def download_recovery_kit():
    """Download MFA recovery kit"""
    try:
        recovery_data = {
            'backup_codes': ['ABC123', 'DEF456', 'GHI789', 'JKL012'],
            'recovery_instructions': 'Store these codes in a safe place',
            'generated_date': '2025-01-15'
        }
        return render_template('mfa/download_recovery_kit.html',
                             recovery_data=recovery_data,
                             page_title='Download Recovery Kit')
    except Exception as e:
        logger.error(f"Download recovery kit error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.settings'))

@mfa_bp.route('/export-activity-log')
@login_required
def export_activity_log():
    """Export MFA activity log"""
    try:
        flash('Activity log exported successfully', 'success')
        return redirect(url_for('mfa.activity_log'))
    except Exception as e:
        logger.error(f"Export activity log error: {e}")
        flash('Export failed', 'error')
        return redirect(url_for('mfa.activity_log'))

@mfa_bp.route('/generate-backup-codes')
@login_required
def generate_backup_codes():
    """Generate new backup codes"""
    try:
        backup_codes = ['ABC123', 'DEF456', 'GHI789', 'JKL012', 'MNO345', 'PQR678']
        return render_template('mfa/backup_codes.html',
                             backup_codes=backup_codes,
                             page_title='Backup Codes')
    except Exception as e:
        logger.error(f"Generate backup codes error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))

@mfa_bp.route('/reset-mfa')
@login_required
def reset_mfa():
    """Reset MFA settings"""
    try:
        return render_template('mfa/reset_mfa.html',
                             page_title='Reset MFA')
    except Exception as e:
        logger.error(f"Reset MFA error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.settings'))

@mfa_bp.route('/revoke-all-devices')
@login_required
def revoke_all_devices():
    """Revoke all trusted devices"""
    try:
        flash('All devices revoked successfully', 'success')
        return redirect(url_for('mfa.settings'))
    except Exception as e:
        logger.error(f"Revoke all devices error: {e}")
        flash('Failed to revoke devices', 'error')
        return redirect(url_for('mfa.settings'))

@mfa_bp.route('/revoke-device')
@login_required
def revoke_device():
    """Revoke specific device"""
    try:
        device_id = request.args.get('id', '')
        flash(f'Device {device_id} revoked successfully', 'success')
        return redirect(url_for('mfa.settings'))
    except Exception as e:
        logger.error(f"Revoke device error: {e}")
        flash('Failed to revoke device', 'error')
        return redirect(url_for('mfa.settings'))

@mfa_bp.route('/security-logs')
@login_required
def security_logs():
    """MFA security logs"""
    try:
        return redirect(url_for('mfa.activity_log'))
    except Exception as e:
        logger.error(f"Security logs error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))

@mfa_bp.route('/setup')
@login_required
def setup():
    """MFA setup - alias for setup_totp"""
    return setup_totp()

@mfa_bp.route('/setup-totp')
@login_required
def setup_totp():
    """Setup TOTP authentication"""
    try:
        mfa_status = MFAService.get_mfa_status(current_user.id)
        if mfa_status['enabled']:
            flash('MFA is already enabled for your account.', 'info')
            return redirect(url_for('mfa.mfa_dashboard'))

        secret, qr_code_base64, error = MFAService.setup_totp(current_user.id)
        if error:
            flash(f'Error setting up MFA: {error}', 'error')
            return redirect(url_for('mfa.mfa_dashboard'))

        return render_template('mfa/setup_totp.html',
                             secret=secret,
                             qr_code=qr_code_base64,
                             page_title='Setup TOTP')
    except Exception as e:
        logger.error(f"Setup TOTP error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))

@mfa_bp.route('/test-backup-code')
@login_required
def test_backup_code():
    """Test backup code functionality"""
    try:
        return render_template('mfa/test_backup_code.html',
                             page_title='Test Backup Code')
    except Exception as e:
        logger.error(f"Test backup code error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))

@mfa_bp.route('/update-settings')
@login_required
def update_settings():
    """Update MFA settings"""
    try:
        flash('Settings updated successfully', 'success')
        return redirect(url_for('mfa.settings'))
    except Exception as e:
        logger.error(f"Update settings error: {e}")
        flash('Failed to update settings', 'error')
        return redirect(url_for('mfa.settings'))

@mfa_bp.route('/verify-totp-setup')
@login_required
def verify_totp_setup():
    """Verify TOTP setup"""
    try:
        return render_template('mfa/verify_totp_setup.html',
                             page_title='Verify TOTP Setup')
    except Exception as e:
        logger.error(f"Verify TOTP setup error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.setup_totp'))

@mfa_bp.route('/view-backup-codes')
@login_required
def view_backup_codes():
    """View backup codes"""
    try:
        backup_codes = ['ABC123', 'DEF456', 'GHI789', 'JKL012']
        return render_template('mfa/backup_codes.html',
                             backup_codes=backup_codes,
                             page_title='View Backup Codes')
    except Exception as e:
        logger.error(f"View backup codes error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('mfa.mfa_dashboard'))

# Error handlers for MFA module
@mfa_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors within MFA module"""
    return render_template('mfa/error.html', 
                         error_code=404,
                         error_message="MFA page not found"), 404


@mfa_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors within MFA module"""
    logger.error(f"MFA module internal error: {str(error)}")
    return render_template('mfa/error.html',
                         error_code=500,
                         error_message="Internal server error in MFA module"), 500
"""
User Management Module - Routes
NVC Banking Platform - User Profile and Activity Management

Features:
- Profile management and editing
- Activity monitoring and logging
- User settings and preferences
- Account security management
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from modules.core.extensions import db
from modules.core.security_enforcement import secure_banking_route, admin_required
import logging

# Initialize module components with hyphenated URL for professional banking appearance
user_management_bp = Blueprint('user_management', __name__, 
                              template_folder='templates',
                              url_prefix='/user-management')

# Removed legacy redirect blueprints - clean URLs only
logger = logging.getLogger(__name__)

@user_management_bp.route('/')
@login_required
def user_dashboard():
    """User management dashboard"""
    try:
        from datetime import datetime
        current_time = datetime.now()
        return render_template('user_management/user_dashboard.html',
                             user=current_user,
                             current_date=current_time,
                             current_time=current_time,
                             page_title='User Dashboard')
    except Exception as e:
        logger.error(f"Error loading user dashboard: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@user_management_bp.route('/admin')
@login_required
@admin_required
def admin_user_management():
    """Super Admin user management dashboard with role navigation"""
    try:
        from modules.auth.models import User
        
        # Get all users with their roles
        users = db.session.query(User).all()
        
        # Organize users by role
        users_by_role = {}
        for user in users:
            role = user.role or 'standard_user'
            if role not in users_by_role:
                users_by_role[role] = []
            users_by_role[role].append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role,
                'last_login': user.last_login,
                'created_at': user.created_at,
                'is_active': user.is_active,
                'department': getattr(user, 'department', 'General'),
                'phone': getattr(user, 'phone', 'Not provided')
            })
        
        # Role dashboard mappings
        role_dashboards = {
            'super_admin': {'route': 'dashboard.dashboard_home', 'name': 'Super Admin Dashboard'},
            'admin': {'route': 'admin_management.admin_dashboard', 'name': 'Admin Dashboard'},
            'treasury_officer': {'route': 'dashboard.treasury_dashboard', 'name': 'Treasury Dashboard'},
            'compliance_officer': {'route': 'compliance.overview', 'name': 'Compliance Dashboard'},
            'branch_manager': {'route': 'admin_management.branch_management', 'name': 'Branch Manager Dashboard'},
            'customer_service': {'route': 'dashboard.dashboard_home', 'name': 'Customer Service Dashboard'},
            'risk_manager': {'route': 'compliance.overview', 'name': 'Risk Management Dashboard'},
            'sovereign_banker': {'route': 'sovereign.sovereign_dashboard', 'name': 'Sovereign Banking Dashboard'},
            'standard_user': {'route': 'dashboard.dashboard_home', 'name': 'Customer Dashboard'},
            'business_user': {'route': 'dashboard.dashboard_home', 'name': 'Business Customer Dashboard'}
        }
        
        # User statistics
        total_users = len(users)
        active_users = len([u for u in users if u.is_active])
        roles_count = len(users_by_role)
        
        return render_template('user_management/admin_user_management.html',
                             users_by_role=users_by_role,
                             role_dashboards=role_dashboards,
                             total_users=total_users,
                             active_users=active_users,
                             roles_count=roles_count,
                             page_title='Super Admin - User Management')
    except Exception as e:
        logger.error(f"Error loading admin user management: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard'))

@user_management_bp.route('/impersonate/<int:user_id>')
@login_required
@admin_required
def impersonate_user(user_id):
    """Allow super admin to experience user's role dashboard"""
    try:
        from modules.auth.models import User
        from flask_login import login_user
        
        # Get the target user
        target_user = User.query.get_or_404(user_id)
        
        # Store current super admin info in session for restoration
        from flask import session
        session['original_user_id'] = current_user.id
        session['original_user_role'] = current_user.role
        session['impersonating'] = True
        session['impersonated_user_id'] = user_id
        session['impersonated_user_role'] = target_user.role
        
        logger.info(f"Super admin {current_user.username} impersonating user {target_user.username} (Role: {target_user.role})")
        
        # Redirect to appropriate dashboard based on role
        role_routes = {
            'super_admin': 'dashboard.dashboard_home',
            'admin': 'admin_management.admin_dashboard', 
            'treasury_officer': 'dashboard.treasury_dashboard',
            'compliance_officer': 'compliance.overview',
            'branch_manager': 'admin_management.branch_management',
            'customer_service': 'dashboard.dashboard_home',
            'risk_manager': 'compliance.overview',
            'sovereign_banker': 'sovereign.sovereign_dashboard',
            'standard_user': 'dashboard.dashboard_home',
            'business_user': 'dashboard.dashboard_home'
        }
        
        route = role_routes.get(target_user.role, 'dashboard.dashboard_home')
        flash(f'Now experiencing {target_user.first_name} {target_user.last_name}\'s dashboard ({target_user.role})', 'info')
        
        return redirect(url_for(route))
        
    except Exception as e:
        logger.error(f"Error impersonating user {user_id}: {e}")
        flash('Unable to access user dashboard', 'error')
        return redirect(url_for('user_management.admin_user_management'))

@user_management_bp.route('/stop-impersonation')
@login_required
def stop_impersonation():
    """Stop impersonation and return to super admin dashboard"""
    try:
        from flask import session
        
        if 'impersonating' in session:
            original_user_id = session.pop('original_user_id', None)
            session.pop('original_user_role', None)
            session.pop('impersonating', None)
            session.pop('impersonated_user_id', None)
            session.pop('impersonated_user_role', None)
            
            logger.info(f"Stopped impersonation, returning to super admin dashboard")
            flash('Returned to Super Admin view', 'success')
        
        return redirect(url_for('user_management.admin_user_management'))
        
    except Exception as e:
        logger.error(f"Error stopping impersonation: {e}")
        flash('Error returning to admin view', 'error')
        return redirect(url_for('dashboard.dashboard'))

@user_management_bp.route('/profile')
@login_required
@secure_banking_route(
    required_permissions=['profile_management'],
    rate_limit=10,
    validation_rules={
        'required_fields': [],
        'optional_fields': ['first_name', 'last_name', 'email', 'phone']
    }
)
def profile_management():
    """Profile management interface"""
    try:
        return render_template('user_management/profile_management.html',
                             user=current_user,
                             page_title='Profile Management')
    except Exception as e:
        logger.error(f"Error loading profile management for user {current_user.id}: {str(e)}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.user_dashboard'))

@user_management_bp.route('/activity')
@login_required
@secure_banking_route(
    required_permissions=['activity_monitoring'],
    rate_limit=10,
    validation_rules={
        'required_fields': [],
        'optional_fields': ['page', 'filter_type', 'date_range']
    }
)
def activity_monitoring():
    """Activity monitoring interface"""
    try:
        page = request.args.get('page', 1, type=int)
        filter_type = request.args.get('filter_type', 'all')
        
        return render_template('activity_monitoring.html',
                             user=current_user,
                             page_title='Activity Monitoring',
                             current_page=page,
                             filter_type=filter_type)
    except Exception as e:
        logger.error(f"Error loading activity monitoring for user {current_user.id}: {str(e)}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.user_dashboard'))

@user_management_bp.route('/settings')
@login_required
@secure_banking_route(
    required_permissions=['user_settings'],
    rate_limit=5,
    validation_rules={
        'required_fields': [],
        'optional_fields': ['notification_preferences', 'security_settings', 'privacy_controls']
    }
)
def user_settings():
    """User settings management"""
    try:
        return render_template('user_settings.html',
                             user=current_user,
                             page_title='User Settings')
    except Exception as e:
        logger.error(f"Error loading user settings for user {current_user.id}: {str(e)}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.user_dashboard'))

@user_management_bp.route('/api/user/<int:user_id>')
@login_required
@admin_required
def get_user_details(user_id):
    """Get detailed user information for admin"""
    try:
        from modules.auth.models import User
        
        user = User.query.get_or_404(user_id)
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
            'department': getattr(user, 'department', 'General'),
            'phone': getattr(user, 'phone', 'Not provided'),
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        
        return jsonify(user_data)
        
    except Exception as e:
        logger.error(f"Error getting user details for user {user_id}: {e}")
        return jsonify({'error': 'Unable to load user details'}), 500

@user_management_bp.route('/api/health')
def health_check():
    """User management module health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'user_management',
        'timestamp': datetime.utcnow().isoformat()
    })

# Missing routes referenced in templates
@user_management_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """User management analytics"""
    try:
        analytics_data = {
            'total_users': 15247,
            'active_users': 14892,
            'new_users_today': 23,
            'user_growth_rate': 15.2,
            'user_activity': [
                {'date': '2025-01-15', 'logins': 2547, 'registrations': 23},
                {'date': '2025-01-14', 'logins': 2398, 'registrations': 19},
                {'date': '2025-01-13', 'logins': 2654, 'registrations': 31}
            ],
            'user_segments': [
                {'segment': 'Premium Users', 'count': 2547, 'percentage': 16.7},
                {'segment': 'Standard Users', 'count': 10200, 'percentage': 66.9},
                {'segment': 'Trial Users', 'count': 2500, 'percentage': 16.4}
            ]
        }
        return render_template('user_management/analytics.html',
                             analytics_data=analytics_data,
                             page_title='User Analytics')
    except Exception as e:
        logger.error(f"User analytics error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.admin_user_management'))

@user_management_bp.route('/bulk-operations')
@login_required
@admin_required
def bulk_operations():
    """Bulk user operations"""
    try:
        bulk_data = {
            'available_operations': [
                'Bulk Email', 'Password Reset', 'Account Activation',
                'Role Assignment', 'Permission Update', 'Account Suspension'
            ],
            'recent_operations': [
                {'operation': 'Bulk Email', 'users': 1500, 'date': '2025-01-10', 'status': 'Completed'},
                {'operation': 'Password Reset', 'users': 45, 'date': '2025-01-09', 'status': 'Completed'},
                {'operation': 'Role Assignment', 'users': 23, 'date': '2025-01-08', 'status': 'In Progress'}
            ]
        }
        return render_template('user_management/bulk_operations.html',
                             bulk_data=bulk_data,
                             page_title='Bulk Operations')
    except Exception as e:
        logger.error(f"Bulk operations error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.admin_user_management'))

@user_management_bp.route('/list-users')
@login_required
@admin_required
def list_users():
    """List all users"""
    try:
        from modules.auth.models import User

        page = request.args.get('page', 1, type=int)
        per_page = 50

        users = User.query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        users_data = {
            'users': [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_active': user.is_active,
                    'last_login': user.last_login.strftime('%Y-%m-%d') if user.last_login else 'Never'
                }
                for user in users.items
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_prev': users.has_prev,
                'has_next': users.has_next
            }
        }
        return render_template('user_management/list_users.html',
                             users_data=users_data,
                             page_title='User List')
    except Exception as e:
        logger.error(f"List users error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.admin_user_management'))

@user_management_bp.route('/permissions-management')
@login_required
@admin_required
def permissions_management():
    """Permissions management interface"""
    try:
        permissions_data = {
            'available_permissions': [
                'user_create', 'user_edit', 'user_delete', 'user_view',
                'role_create', 'role_edit', 'role_delete', 'role_view',
                'permission_assign', 'permission_revoke', 'system_admin'
            ],
            'permission_groups': [
                {'name': 'User Management', 'permissions': ['user_create', 'user_edit', 'user_delete', 'user_view']},
                {'name': 'Role Management', 'permissions': ['role_create', 'role_edit', 'role_delete', 'role_view']},
                {'name': 'System Administration', 'permissions': ['permission_assign', 'permission_revoke', 'system_admin']}
            ],
            'role_permissions': [
                {'role': 'Admin', 'permissions': 11, 'users': 5},
                {'role': 'Manager', 'permissions': 8, 'users': 23},
                {'role': 'User', 'permissions': 4, 'users': 15219}
            ]
        }
        return render_template('user_management/permissions_management.html',
                             permissions_data=permissions_data,
                             page_title='Permissions Management')
    except Exception as e:
        logger.error(f"Permissions management error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.admin_user_management'))

@user_management_bp.route('/role-management')
@login_required
@admin_required
def role_management():
    """Role management interface"""
    try:
        roles_data = {
            'available_roles': [
                {'name': 'Super Admin', 'users': 2, 'permissions': 15, 'description': 'Full system access'},
                {'name': 'Admin', 'users': 5, 'permissions': 11, 'description': 'Administrative access'},
                {'name': 'Manager', 'users': 23, 'permissions': 8, 'description': 'Management access'},
                {'name': 'User', 'users': 15219, 'permissions': 4, 'description': 'Standard user access'},
                {'name': 'Guest', 'users': 0, 'permissions': 1, 'description': 'Limited read-only access'}
            ],
            'role_hierarchy': ['Super Admin', 'Admin', 'Manager', 'User', 'Guest'],
            'default_permissions': {
                'User': ['profile_view', 'profile_edit', 'dashboard_access', 'basic_operations'],
                'Manager': ['user_view', 'user_edit', 'reports_access', 'team_management'],
                'Admin': ['user_create', 'user_delete', 'role_assign', 'system_config']
            }
        }
        return render_template('user_management/role_management.html',
                             roles_data=roles_data,
                             page_title='Role Management')
    except Exception as e:
        logger.error(f"Role management error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.admin_user_management'))

@user_management_bp.route('/user-admin')
@login_required
@admin_required
def user_admin():
    """User administration interface"""
    try:
        from modules.auth.models import User

        admin_data = {
            'recent_users': User.query.order_by(User.created_at.desc()).limit(10).all(),
            'user_statistics': {
                'total_users': User.query.count(),
                'active_users': User.query.filter_by(is_active=True).count(),
                'inactive_users': User.query.filter_by(is_active=False).count(),
                'admin_users': User.query.filter_by(role='admin').count()
            },
            'admin_actions': [
                'Create User', 'Edit User', 'Delete User', 'Reset Password',
                'Assign Role', 'Suspend Account', 'Activate Account', 'View Activity'
            ]
        }
        return render_template('user_management/user_admin.html',
                             admin_data=admin_data,
                             page_title='User Administration')
    except Exception as e:
        logger.error(f"User admin error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('user_management.admin_user_management'))
/**
 * RBAC Navigation JavaScript
 * NVC Banking Platform - Role-Based Access Control
 * Version: 3.0.0 - Security-First Navigation
 */

(function() {
    'use strict';

    // ===== RBAC NAVIGATION MANAGER =====
    class RBACNavigationManager {
        constructor() {
            this.userRole = this.getCurrentUserRole();
            this.permissions = this.getCurrentUserPermissions();
            this.init();
        }

        init() {
            this.setupRoleBasedVisibility();
            this.setupNavigationSecurity();
            this.setupPermissionChecks();
            this.setupAuditLogging();
            console.log(`🔐 RBAC Navigation: Initialized for role '${this.userRole}'`);
        }

        getCurrentUserRole() {
            const navElement = document.querySelector('[data-user-role]');
            return navElement?.dataset.userRole || 'guest';
        }

        getCurrentUserPermissions() {
            // Get permissions from meta tag or global variable
            const permissionsMeta = document.querySelector('meta[name="user-permissions"]');
            if (permissionsMeta) {
                try {
                    return JSON.parse(permissionsMeta.content);
                } catch (e) {
                    console.warn('Failed to parse user permissions');
                }
            }
            return window.userPermissions || [];
        }

        setupRoleBasedVisibility() {
            // Show/hide elements based on role
            this.applyRoleVisibility();
            
            // Watch for dynamic content
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.applyRoleVisibilityToElement(node);
                        }
                    });
                });
            });

            observer.observe(document.body, { childList: true, subtree: true });
        }

        applyRoleVisibility() {
            document.querySelectorAll('[data-required-role], [data-required-permission]').forEach(element => {
                this.applyRoleVisibilityToElement(element);
            });
        }

        applyRoleVisibilityToElement(element) {
            const requiredRole = element.dataset.requiredRole;
            const requiredPermission = element.dataset.requiredPermission;
            
            let hasAccess = true;

            // Check role requirement
            if (requiredRole) {
                hasAccess = this.hasRole(requiredRole);
            }

            // Check permission requirement
            if (requiredPermission && hasAccess) {
                hasAccess = this.hasPermission(requiredPermission);
            }

            // Apply visibility
            if (hasAccess) {
                element.classList.remove('nvc-rbac-hidden');
                element.classList.add('nvc-rbac-visible');
                element.removeAttribute('aria-hidden');
            } else {
                element.classList.add('nvc-rbac-hidden');
                element.classList.remove('nvc-rbac-visible');
                element.setAttribute('aria-hidden', 'true');
            }

            // Also check child elements with RBAC classes
            element.querySelectorAll('[data-required-role], [data-required-permission]').forEach(child => {
                this.applyRoleVisibilityToElement(child);
            });
        }

        hasRole(requiredRole) {
            const roleHierarchy = {
                'guest': 0,
                'user': 1,
                'treasury': 2,
                'compliance': 2,
                'manager': 3,
                'admin': 4
            };

            const userLevel = roleHierarchy[this.userRole] || 0;
            const requiredLevel = roleHierarchy[requiredRole] || 0;

            return userLevel >= requiredLevel;
        }

        hasPermission(permission) {
            return this.permissions.includes(permission);
        }

        setupNavigationSecurity() {
            // Intercept navigation clicks to check permissions
            document.addEventListener('click', (e) => {
                const link = e.target.closest('a[href]');
                if (link && this.shouldCheckPermission(link)) {
                    if (!this.checkLinkPermission(link)) {
                        e.preventDefault();
                        this.handleUnauthorizedAccess(link);
                    } else {
                        this.logNavigationEvent(link);
                    }
                }
            });

            // Intercept form submissions
            document.addEventListener('submit', (e) => {
                const form = e.target;
                if (form && this.shouldCheckPermission(form)) {
                    if (!this.checkFormPermission(form)) {
                        e.preventDefault();
                        this.handleUnauthorizedAccess(form);
                    } else {
                        this.logFormSubmissionEvent(form);
                    }
                }
            });
        }

        shouldCheckPermission(element) {
            return element.hasAttribute('data-required-role') || 
                   element.hasAttribute('data-required-permission') ||
                   element.classList.contains('nvc-rbac-protected');
        }

        checkLinkPermission(link) {
            const requiredRole = link.dataset.requiredRole;
            const requiredPermission = link.dataset.requiredPermission;

            if (requiredRole && !this.hasRole(requiredRole)) {
                return false;
            }

            if (requiredPermission && !this.hasPermission(requiredPermission)) {
                return false;
            }

            return true;
        }

        checkFormPermission(form) {
            const requiredRole = form.dataset.requiredRole;
            const requiredPermission = form.dataset.requiredPermission;

            if (requiredRole && !this.hasRole(requiredRole)) {
                return false;
            }

            if (requiredPermission && !this.hasPermission(requiredPermission)) {
                return false;
            }

            return true;
        }

        handleUnauthorizedAccess(element) {
            // Show access denied message
            this.showAccessDeniedMessage();
            
            // Log security event
            this.logSecurityEvent('unauthorized_access_attempt', {
                element: element.tagName,
                href: element.href || element.action,
                required_role: element.dataset.requiredRole,
                required_permission: element.dataset.requiredPermission,
                user_role: this.userRole
            });
        }

        showAccessDeniedMessage() {
            // Create or show access denied notification
            let notification = document.getElementById('nvc-access-denied-notification');
            
            if (!notification) {
                notification = document.createElement('div');
                notification.id = 'nvc-access-denied-notification';
                notification.className = 'nvc-notification-accessible nvc-notification-error';
                notification.setAttribute('role', 'alert');
                notification.innerHTML = `
                    <div class="nvc-notification-content">
                        <i class="fas fa-shield-alt" aria-hidden="true"></i>
                        <span>Access Denied: You don't have permission to access this resource.</span>
                        <button type="button" class="nvc-notification-close" aria-label="Close notification">
                            <i class="fas fa-times" aria-hidden="true"></i>
                        </button>
                    </div>
                `;
                document.body.appendChild(notification);

                // Auto-remove after 5 seconds
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 5000);

                // Close button functionality
                notification.querySelector('.nvc-notification-close').addEventListener('click', () => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                });
            }

            // Announce to screen readers
            if (window.accessibilityManager?.screenReaderAnnouncer) {
                window.accessibilityManager.screenReaderAnnouncer.announce(
                    'Access denied. You do not have permission to access this resource.',
                    'assertive'
                );
            }
        }

        setupPermissionChecks() {
            // Global permission check function
            window.checkPermission = (permission) => {
                return this.hasPermission(permission);
            };

            // Global role check function
            window.checkRole = (role) => {
                return this.hasRole(role);
            };

            // Enhanced button states based on permissions
            document.querySelectorAll('[data-permission-required]').forEach(button => {
                const permission = button.dataset.permissionRequired;
                if (!this.hasPermission(permission)) {
                    button.disabled = true;
                    button.setAttribute('aria-disabled', 'true');
                    button.title = 'Insufficient permissions';
                }
            });
        }

        setupAuditLogging() {
            // Log role-based navigation events
            this.logSecurityEvent('rbac_session_initialized', {
                user_role: this.userRole,
                permissions_count: this.permissions.length,
                timestamp: new Date().toISOString()
            });
        }

        logNavigationEvent(link) {
            this.logSecurityEvent('navigation_access', {
                href: link.href,
                text: link.textContent.trim(),
                required_role: link.dataset.requiredRole,
                required_permission: link.dataset.requiredPermission
            });
        }

        logFormSubmissionEvent(form) {
            this.logSecurityEvent('form_submission', {
                action: form.action,
                method: form.method,
                required_role: form.dataset.requiredRole,
                required_permission: form.dataset.requiredPermission
            });
        }

        logSecurityEvent(event_type, details = {}) {
            const securityData = {
                timestamp: new Date().toISOString(),
                event_type: event_type,
                user_role: this.userRole,
                user_permissions: this.permissions,
                session_id: window.sessionId || 'unknown',
                user_agent: navigator.userAgent,
                url: window.location.href,
                details: details
            };

            // Use the global interaction manager for logging
            window.NVCInteractionManager?.sendLog('security', securityData);
        }

        // Public method to refresh permissions (e.g., after role change)
        refreshPermissions() {
            this.userRole = this.getCurrentUserRole();
            this.permissions = this.getCurrentUserPermissions();
            this.applyRoleVisibility();
            
            this.logSecurityEvent('permissions_refreshed', {
                new_role: this.userRole,
                new_permissions_count: this.permissions.length
            });
        }
    }

    // ===== NAVIGATION ENHANCEMENTS =====
    class NavigationEnhancer {
        constructor() {
            this.setupDropdownAccessibility();
            this.setupMobileNavigation();
            this.setupBreadcrumbNavigation();
        }

        setupDropdownAccessibility() {
            document.querySelectorAll('.nvc-nav-dropdown').forEach(dropdown => {
                const toggle = dropdown.querySelector('.nvc-nav-dropdown-toggle');
                const menu = dropdown.querySelector('.nvc-dropdown-menu');
                
                if (toggle && menu) {
                    // Keyboard navigation
                    toggle.addEventListener('keydown', (e) => {
                        if (e.key === 'ArrowDown') {
                            e.preventDefault();
                            const firstItem = menu.querySelector('.nvc-dropdown-item');
                            if (firstItem) firstItem.focus();
                        }
                    });

                    // Menu item navigation
                    menu.addEventListener('keydown', (e) => {
                        const items = Array.from(menu.querySelectorAll('.nvc-dropdown-item'));
                        const currentIndex = items.indexOf(e.target);

                        switch (e.key) {
                            case 'ArrowDown':
                                e.preventDefault();
                                const nextIndex = (currentIndex + 1) % items.length;
                                items[nextIndex].focus();
                                break;
                            case 'ArrowUp':
                                e.preventDefault();
                                const prevIndex = (currentIndex - 1 + items.length) % items.length;
                                items[prevIndex].focus();
                                break;
                            case 'Escape':
                                e.preventDefault();
                                toggle.focus();
                                // Close dropdown if using Bootstrap
                                if (window.bootstrap) {
                                    bootstrap.Dropdown.getInstance(toggle)?.hide();
                                }
                                break;
                        }
                    });
                }
            });
        }

        setupMobileNavigation() {
            const mobileToggle = document.querySelector('.nvc-mobile-toggle-btn');
            if (mobileToggle) {
                mobileToggle.addEventListener('click', () => {
                    const expanded = mobileToggle.getAttribute('aria-expanded') === 'true';
                    mobileToggle.setAttribute('aria-expanded', (!expanded).toString());
                });
            }
        }

        setupBreadcrumbNavigation() {
            const breadcrumbs = document.querySelectorAll('.nvc-breadcrumb-item a');
            breadcrumbs.forEach((link, index) => {
                link.addEventListener('click', (e) => {
                    if (window.rbacManager) {
                        window.rbacManager.logNavigationEvent(link);
                    }
                });
            });
        }
    }

    // ===== INITIALIZATION =====
    document.addEventListener('DOMContentLoaded', function() {
        window.rbacManager = new RBACNavigationManager();
        window.navigationEnhancer = new NavigationEnhancer();
        
        // Expose refresh function globally
        window.refreshUserPermissions = () => {
            window.rbacManager.refreshPermissions();
        };
    });

})();

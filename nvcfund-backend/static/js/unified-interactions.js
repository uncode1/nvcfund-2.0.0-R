/**
 * NVC Banking Platform - Unified Interactions System
 * Handles all click events, navigation, and user interactions
 * Version: 2.0
 */

class NVCInteractionManager {
    constructor() {
        this.isInitialized = false;
        this.clickHandlers = new Map();
        this.navigationHandlers = new Map();
        this.formHandlers = new Map();
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }

    initialize() {
        if (this.isInitialized) return;
        
        console.log('🏦 NVC Banking Platform - Initializing Interaction Manager');
        
        // Initialize all interaction systems
        this.initializeClickHandlers();
        this.initializeNavigationHandlers();
        this.initializeFormHandlers();
        this.initializeTooltips();
        this.initializeModals();
        this.initializeAlerts();
        this.initializeLoadingStates();
        
        this.isInitialized = true;
        console.log('✅ NVC Interaction Manager initialized successfully');
    }

    /**
     * Initialize click handlers for all interactive elements
     */
    initializeClickHandlers() {
        // Handle all button clicks
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-action]');
            if (target) {
                this.handleActionClick(e, target);
            }
        });

        // Handle navigation links
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href]');
            if (link && !link.hasAttribute('data-no-track')) {
                this.handleNavigationClick(e, link);
            }
        });

        // Handle card clicks
        document.addEventListener('click', (e) => {
            const card = e.target.closest('.nvc-card[data-href]');
            if (card) {
                this.handleCardClick(e, card);
            }
        });

        // Handle dropdown toggles
        document.addEventListener('click', (e) => {
            const dropdown = e.target.closest('[data-bs-toggle="dropdown"]');
            if (dropdown) {
                this.handleDropdownClick(e, dropdown);
            }
        });
    }

    /**
     * Handle action button clicks
     */
    handleActionClick(event, element) {
        const action = element.getAttribute('data-action');
        const target = element.getAttribute('data-target');
        const confirm = element.getAttribute('data-confirm');
        
        // Log the action
        this.logUserAction('button_click', action, element);
        
        // Show confirmation if required
        if (confirm && !window.confirm(confirm)) {
            event.preventDefault();
            return false;
        }
        
        // Add loading state
        this.setLoadingState(element, true);
        
        // Handle specific actions
        switch (action) {
            case 'transfer':
                this.handleTransferAction(element, target);
                break;
            case 'card-block':
                this.handleCardBlockAction(element, target);
                break;
            case 'card-unblock':
                this.handleCardUnblockAction(element, target);
                break;
            case 'export-data':
                this.handleExportAction(element, target);
                break;
            case 'create-account':
                this.handleCreateAccountAction(element, target);
                break;
            case 'apply-loan':
                this.handleLoanApplicationAction(element, target);
                break;
            case 'dismiss-notification':
                this.handleDismissNotification(element, target);
                break;
            case 'reload-page':
                this.handleReloadPage(element, target);
                break;
            case 'go-back':
                this.handleGoBack(element, target);
                break;
            
        // Additional handlers for converted onclick patterns
        case 'confirm':
            if (window.confirm(target || 'Are you sure?')) {
                const callback = element.getAttribute('data-callback');
                if (callback) {
                    eval(callback);
                }
            }
            break;
            
        case 'toggle-visibility':
            const toggleTarget = document.querySelector(target);
            if (toggleTarget) {
                toggleTarget.style.display = toggleTarget.style.display === 'none' ? 'block' : 'none';
            }
            break;
            
        case 'toggle-class':
            const classTarget = document.querySelector(target);
            const className = element.getAttribute('data-class');
            if (classTarget && className) {
                classTarget.classList.toggle(className);
            }
            break;
            
        case 'load-content':
            const url = element.getAttribute('data-url');
            if (url) {
                this.loadContent(url, target);
            }
            break;
            
        case 'fetch-data':
            const fetchUrl = element.getAttribute('data-url');
            if (fetchUrl) {
                this.fetchData(fetchUrl);
            }
            break;
            
        case 'update-content':
            const updateUrl = element.getAttribute('data-url');
            if (updateUrl && target) {
                this.updateContent(target, updateUrl);
            }
            break;
            
        case 'view-account':
            const accountId = element.getAttribute('data-account');
            if (accountId) {
                this.viewAccount(accountId);
            }
            break;
            
        case 'download-statement':
            const statementAccount = element.getAttribute('data-account');
            if (statementAccount) {
                this.downloadStatement(statementAccount);
            }
            break;

            default:
                this.handleGenericAction(element, action, target);
        }
    }

    /**
     * Handle navigation link clicks
     */
    handleNavigationClick(event, link) {
        const href = link.getAttribute('href');
        const text = link.textContent.trim();
        
        // Skip external links and anchors
        if (href.startsWith('http') || href.startsWith('#')) {
            return;
        }
        
        // Log navigation
        this.logUserAction('navigation_click', text, link, href);
        
        // Add visual feedback
        this.addNavigationFeedback(link);
    }

    /**
     * Handle card clicks for navigation
     */
    handleCardClick(event, card) {
        const href = card.getAttribute('data-href');
        const title = card.querySelector('.nvc-card-title')?.textContent || 'Card';
        
        this.logUserAction('card_click', title, card, href);
        
        // Add click animation
        card.style.transform = 'scale(0.98)';
        setTimeout(() => {
            card.style.transform = '';
            if (href) {
                window.location.href = href;
            }
        }, 150);
    }

    /**
     * Initialize navigation handlers
     */
    initializeNavigationHandlers() {
        // Handle mobile navigation toggle
        const mobileToggle = document.querySelector('.nvc-mobile-toggle-btn');
        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => {
                this.logUserAction('mobile_menu_toggle', 'open', mobileToggle);
            });
        }

        // Handle search functionality
        const searchInput = document.querySelector('.nvc-search-input');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.handleSearch(e.target.value);
                }, 300);
            });
        }

        // Handle breadcrumb navigation
        document.addEventListener('click', (e) => {
            const breadcrumb = e.target.closest('.breadcrumb-item a');
            if (breadcrumb) {
                this.logUserAction('breadcrumb_click', breadcrumb.textContent, breadcrumb);
            }
        });
    }

    /**
     * Initialize form handlers
     */
    initializeFormHandlers() {
        // Handle form submissions
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.tagName === 'FORM') {
                this.handleFormSubmission(e, form);
            }
        });

        // Handle form input changes
        document.addEventListener('change', (e) => {
            const input = e.target;
            if (input.closest('form')) {
                this.handleFormInputChange(e, input);
            }
        });

        // Handle form validation
        document.addEventListener('invalid', (e) => {
            this.handleFormValidation(e, e.target);
        }, true);
    }

    /**
     * Handle form submissions
     */
    handleFormSubmission(event, form) {
        const formId = form.id || 'unknown';
        const action = form.action || window.location.href;
        
        this.logUserAction('form_submit', formId, form, action);
        
        // Add loading state to submit button
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
            this.setLoadingState(submitBtn, true);
        }
        
        // Validate form before submission
        if (!this.validateForm(form)) {
            event.preventDefault();
            if (submitBtn) {
                this.setLoadingState(submitBtn, false);
            }
            return false;
        }
    }

    /**
     * Initialize tooltips
     */
    initializeTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    /**
     * Initialize modals
     */
    initializeModals() {
        // Handle modal open events
        document.addEventListener('show.bs.modal', (e) => {
            const modal = e.target;
            const modalId = modal.id || 'unknown';
            this.logUserAction('modal_open', modalId, modal);
        });

        // Handle modal close events
        document.addEventListener('hide.bs.modal', (e) => {
            const modal = e.target;
            const modalId = modal.id || 'unknown';
            this.logUserAction('modal_close', modalId, modal);
        });
    }

    /**
     * Initialize alert handling
     */
    initializeAlerts() {
        // Auto-dismiss success and info alerts
        setTimeout(() => {
            const alerts = document.querySelectorAll('.nvc-alert-success, .nvc-alert-info');
            alerts.forEach(alert => {
                this.dismissAlert(alert);
            });
        }, 5000);

        // Handle alert close buttons
        document.addEventListener('click', (e) => {
            const closeBtn = e.target.closest('.nvc-alert-close');
            if (closeBtn) {
                const alert = closeBtn.closest('.nvc-alert');
                if (alert) {
                    this.dismissAlert(alert);
                }
            }
        });
    }

    /**
     * Initialize loading states
     */
    initializeLoadingStates() {
        // Handle loading buttons
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.nvc-btn-loading');
            if (btn && btn.type === 'submit') {
                // Loading state will be handled by form submission
                return;
            }
        });
    }

    /**
     * Set loading state for elements
     */
    setLoadingState(element, isLoading) {
        if (isLoading) {
            element.classList.add('loading');
            element.disabled = true;
        } else {
            element.classList.remove('loading');
            element.disabled = false;
        }
    }

    /**
     * Add navigation feedback
     */
    addNavigationFeedback(link) {
        link.style.transform = 'translateY(-1px)';
        setTimeout(() => {
            link.style.transform = '';
        }, 200);
    }

    /**
     * Handle search functionality
     */
    handleSearch(query) {
        if (query.length < 2) return;
        
        this.logUserAction('search', query);
        
        // Implement search logic here
        console.log('Searching for:', query);
    }

    /**
     * Validate form
     */
    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });
        
        return isValid;
    }

    /**
     * Show field error
     */
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        let errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentNode.appendChild(errorElement);
        }
        errorElement.textContent = message;
    }

    /**
     * Clear field error
     */
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }
    }

    /**
     * Dismiss alert
     */
    dismissAlert(alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(100%)';
        setTimeout(() => {
            alert.remove();
        }, 300);
    }

    /**
     * Log user actions for debugging
     */
    logUserAction(type, action, element = null, target = null) {
        const logData = {
            type: type,
            action: action,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent.substring(0, 100)
        };
        
        if (element) {
            logData.elementId = element.id;
            logData.elementClass = element.className;
            logData.elementTag = element.tagName;
        }
        
        if (target) {
            logData.target = target;
        }
        
        // Log to console for debugging
        console.log('🎯 User Action:', logData);
        
        // Send to server if endpoint exists
        this.sendActionLog(logData);
    }

    /**
     * Send action log to server
     */
    async sendLog(logType, logData) {
        try {
            // Use a generic, centralized logging endpoint
            const response = await fetch(`/api/log/${logType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(logData)
            });
            
            if (!response.ok) {
                console.warn(`Failed to log ${logType} event to server`);
            }
        } catch (error) {
            console.warn(`Error logging ${logType} event:`, error);
        }
    }

    /**
     * Get CSRF token
     */
    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }

    /**
     * Specific action handlers
     */
    handleTransferAction(element, target) {
        console.log('Handling transfer action');
        // Implement transfer logic
        setTimeout(() => this.setLoadingState(element, false), 2000);
    }

    handleCardBlockAction(element, target) {
        console.log('Handling card block action');
        // Implement card blocking logic
        setTimeout(() => this.setLoadingState(element, false), 1500);
    }

    handleCardUnblockAction(element, target) {
        console.log('Handling card unblock action');
        // Implement card unblocking logic
        setTimeout(() => this.setLoadingState(element, false), 1500);
    }

    handleExportAction(element, target) {
        console.log('Handling export action');
        // Implement export logic
        setTimeout(() => this.setLoadingState(element, false), 3000);
    }

    handleCreateAccountAction(element, target) {
        console.log('Handling create account action');
        // Implement account creation logic
        setTimeout(() => this.setLoadingState(element, false), 2500);
    }

    handleLoanApplicationAction(element, target) {
        console.log('Handling loan application action');
        // Implement loan application logic
        setTimeout(() => this.setLoadingState(element, false), 3000);
    }

    handleGenericAction(element, action, target) {
        console.log('Handling generic action:', action);
        // Implement generic action logic
        setTimeout(() => this.setLoadingState(element, false), 1000);
    }

    handleDismissNotification(element, target) {
        console.log('Dismissing notification');
        const notification = element.closest('.nvc-notification, .alert, .nvc-alert');
        if (notification) {
            this.dismissAlert(notification);
        }
        this.setLoadingState(element, false);
    }

    handleReloadPage(element, target) {
        console.log('Reloading page');
        this.setLoadingState(element, false);
        window.location.reload();
    }

    handleGoBack(element, target) {
        console.log('Going back');
        this.setLoadingState(element, false);
        window.history.back();
    }

    /**
     * Utility methods
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `nvc-alert nvc-alert-${type}`;
        notification.innerHTML = `
            <i class="nvc-alert-icon fas fa-info-circle"></i>
            <span class="nvc-alert-message">${message}</span>
            <button type="button" class="nvc-alert-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        const container = document.querySelector('.nvc-flash-container') || document.body;
        container.appendChild(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            this.dismissAlert(notification);
        }, 5000);
    }

    showModal(title, content, actions = []) {
        // Create modal dynamically
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                    <div class="modal-footer">
                        ${actions.map(action => `<button type="button" class="btn ${action.class}" ${action.dismiss ? 'data-bs-dismiss="modal"' : ''}>${action.text}</button>`).join('')}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show modal
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            // Remove modal after hiding
            modal.addEventListener('hidden.bs.modal', () => {
                modal.remove();
            });
        }
    }
}

// Initialize the interaction manager
const nvcInteractionManager = new NVCInteractionManager();

// Export for global access
window.NVCInteractionManager = nvcInteractionManager;

// Utility functions for backward compatibility
window.logUserAction = (action, element, target) => {
    nvcInteractionManager.logUserAction('legacy_action', action, element, target);
};

window.showNotification = (message, type) => {
    nvcInteractionManager.showNotification(message, type);
};

window.showModal = (title, content, actions) => {
    nvcInteractionManager.showModal(title, content, actions);
};
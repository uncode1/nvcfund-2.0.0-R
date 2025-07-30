/**
 * NVC Banking Platform - Public Routes Unified JavaScript
 * Centralized JavaScript for all public-facing pages
 * Version: 1.0.0 - Complete Public Interaction System
 */

// Import base interaction system
if (typeof window.NVCInteractionManager !== 'undefined') {
    console.log('🔗 Base NVC Interaction Manager detected');
}

/**
 * Public Page Interaction Manager
 * Handles all public page interactions, animations, and functionality
 */
class NVCPublicManager {
    constructor() {
        this.isInitialized = false;
        this.liveDataStream = null;
        this.animationObserver = null;
        this.scrollHandler = null;
        
        // Configuration
        this.config = {
            animationDelay: 100,
            scrollThreshold: 0.1,
            liveDataInterval: 30000,
            retryAttempts: 3,
            retryDelay: 5000
        };
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }
    
    initialize() {
        if (this.isInitialized) return;
        
        console.log('🏦 NVC Public Manager - Initializing...');
        
        try {
            // Initialize all public page systems
            this.initializeScrollAnimations();
            this.initializeNavigationHandlers();
            this.initializeFormHandlers();
            this.initializeButtonInteractions();
            this.initializeTooltips();
            this.initializeModals();
            this.initializeLiveDataStream();
            this.initializePerformanceOptimizations();
            
            this.isInitialized = true;
            console.log('✅ NVC Public Manager initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing NVC Public Manager:', error);
        }
    }
    
    /**
     * Initialize scroll-based animations (DISABLED to prevent flashing)
     */
    initializeScrollAnimations() {
        // DISABLED: This was causing content to flash/disappear on page load
        // The original animation system would hide elements with opacity: 0 initially
        // causing a flash of invisible content before animations kicked in

        console.log('📱 Scroll animations disabled to prevent content flashing');

        // Instead, ensure all content is immediately visible
        const animatableElements = document.querySelectorAll(
            '.nvc-feature-card, .nvc-innovation-card, .nvc-service-card, .nvc-stat-card, .nvc-section-title, .nvc-section-subtitle'
        );

        animatableElements.forEach((element) => {
            // Ensure all elements are immediately visible
            element.style.opacity = '1';
            element.style.transform = 'none';
            element.style.transition = 'none';
        });

        console.log(`📱 Made ${animatableElements.length} elements immediately visible`);
    }
    
    /**
     * Initialize navigation handlers
     */
    initializeNavigationHandlers() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Active navigation highlighting
        this.initializeActiveNavigation();
        
        console.log('🧭 Navigation handlers initialized');
    }
    
    /**
     * Initialize form handlers
     */
    initializeFormHandlers() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Add loading states
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    submitBtn.classList.add('nvc-loading');
                    submitBtn.disabled = true;
                    
                    // Add loading text
                    const originalText = submitBtn.textContent;
                    submitBtn.textContent = 'Processing...';
                    
                    // Reset after timeout (fallback)
                    setTimeout(() => {
                        submitBtn.classList.remove('nvc-loading');
                        submitBtn.disabled = false;
                        submitBtn.textContent = originalText;
                    }, 10000);
                }
            });
            
            // Real-time validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.clearFieldError(input));
            });
        });
        
        console.log(`📝 Form handlers initialized for ${forms.length} forms`);
    }
    
    /**
     * Initialize button interactions
     */
    initializeButtonInteractions() {
        const buttons = document.querySelectorAll('.nvc-btn');
        
        buttons.forEach(button => {
            // Add ripple effect
            button.addEventListener('click', (e) => {
                this.createRippleEffect(e, button);
            });
            
            // Add hover analytics
            button.addEventListener('mouseenter', () => {
                this.logUserAction('button_hover', button.textContent.trim(), button.href || button.getAttribute('data-target'));
            });
        });
        
        console.log(`🔘 Button interactions initialized for ${buttons.length} buttons`);
    }
    
    /**
     * Initialize tooltips
     */
    initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"], [title]');
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            tooltipElements.forEach(element => {
                new bootstrap.Tooltip(element);
            });
            console.log(`💬 Tooltips initialized for ${tooltipElements.length} elements`);
        }
    }
    
    /**
     * Initialize modals
     */
    initializeModals() {
        const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
        
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                this.logUserAction('modal_open', trigger.getAttribute('data-bs-target'));
            });
        });
        
        console.log(`🪟 Modal handlers initialized for ${modalTriggers.length} triggers`);
    }
    
    /**
     * Initialize live data stream (DISABLED to prevent flashing)
     */
    initializeLiveDataStream() {
        // DISABLED: Live data stream was causing content flashing during API calls
        // The WebSocket connections and HTTP polling were causing UI updates that
        // resulted in visible content changes and flashing

        console.log('📡 Live data stream disabled to prevent content flashing');

        // Keep static content visible without dynamic updates
        // Users can refresh the page manually to get updated data
    }
    
    /**
     * Initialize performance optimizations
     */
    initializePerformanceOptimizations() {
        // Lazy load images
        this.initializeLazyLoading();
        
        // Optimize scroll performance
        this.initializeScrollOptimization();
        
        // Preload critical resources
        this.preloadCriticalResources();
        
        console.log('⚡ Performance optimizations initialized');
    }
    
    /**
     * Initialize lazy loading for images
     */
    initializeLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }
    
    /**
     * Initialize scroll optimization
     */
    initializeScrollOptimization() {
        let ticking = false;
        
        this.scrollHandler = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.handleScroll();
                    ticking = false;
                });
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', this.scrollHandler, { passive: true });
    }
    
    /**
     * Handle scroll events
     */
    handleScroll() {
        const scrollY = window.scrollY;
        
        // Update navigation active state
        this.updateActiveNavigation(scrollY);
        
        // Parallax effects (if needed)
        this.updateParallaxEffects(scrollY);
    }
    
    /**
     * Initialize active navigation
     */
    initializeActiveNavigation() {
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link[href^="#"]');
        this.navSections = Array.from(navLinks).map(link => {
            const href = link.getAttribute('href');
            const section = document.querySelector(href);
            return { link, section, href };
        }).filter(item => item.section);
    }
    
    /**
     * Update active navigation based on scroll position
     */
    updateActiveNavigation(scrollY) {
        if (!this.navSections) return;
        
        const current = this.navSections.find(item => {
            const rect = item.section.getBoundingClientRect();
            return rect.top <= 100 && rect.bottom >= 100;
        });
        
        this.navSections.forEach(item => {
            item.link.classList.toggle('active', item === current);
        });
    }
    
    /**
     * Update parallax effects
     */
    updateParallaxEffects(scrollY) {
        const parallaxElements = document.querySelectorAll('.nvc-parallax');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            const yPos = -(scrollY * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }
    
    /**
     * Preload critical resources
     */
    preloadCriticalResources() {
        const criticalResources = [
            '/static/css/public-unified.css',
            '/static/js/public-unified.js'
        ];
        
        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource;
            link.as = resource.endsWith('.css') ? 'style' : 'script';
            document.head.appendChild(link);
        });
    }
    
    /**
     * Create ripple effect for buttons
     */
    createRippleEffect(event, button) {
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('nvc-ripple');
        
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
    
    /**
     * Validate form field
     */
    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        let isValid = true;
        let message = '';
        
        // Basic validation rules
        if (field.required && !value) {
            isValid = false;
            message = 'This field is required';
        } else if (type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            message = 'Please enter a valid email address';
        }
        
        this.setFieldValidation(field, isValid, message);
        return isValid;
    }
    
    /**
     * Clear field error
     */
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.remove();
        }
    }
    
    /**
     * Set field validation state
     */
    setFieldValidation(field, isValid, message) {
        this.clearFieldError(field);
        
        if (!isValid) {
            field.classList.add('is-invalid');
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = message;
            field.parentNode.appendChild(feedback);
        }
    }
    
    /**
     * Validate email format
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    /**
     * Log user actions for analytics
     */
    logUserAction(action, details, target) {
        if (typeof window.NVCInteractionManager !== 'undefined') {
            window.NVCInteractionManager.logUserAction('public_page', action, details, target);
        } else {
            console.log(`📊 User Action: ${action}`, { details, target });
        }
    }
    
    /**
     * Cleanup method
     */
    destroy() {
        if (this.animationObserver) {
            this.animationObserver.disconnect();
        }
        
        if (this.scrollHandler) {
            window.removeEventListener('scroll', this.scrollHandler);
        }
        
        if (this.liveDataStream && typeof this.liveDataStream.destroy === 'function') {
            this.liveDataStream.destroy();
        }
        
        this.isInitialized = false;
        console.log('🛑 NVC Public Manager destroyed');
    }
}

// Initialize the public manager
const nvcPublicManager = new NVCPublicManager();

// Export for global access
window.NVCPublicManager = nvcPublicManager;

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.NVCPublicManager) {
        window.NVCPublicManager.destroy();
    }
});

// Utility functions for backward compatibility
window.logPublicAction = (action, details, target) => {
    nvcPublicManager.logUserAction(action, details, target);
};

console.log('🚀 NVC Public Unified JavaScript loaded successfully');

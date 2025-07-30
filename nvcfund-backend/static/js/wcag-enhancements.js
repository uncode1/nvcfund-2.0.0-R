/**
 * WCAG AA+ Accessibility Enhancements
 * NVC Banking Platform - Accessibility First
 * Version: 3.0.0 - WCAG 2.1 Level AA+ Compliant
 */

(function() {
    'use strict';

    // ===== ACCESSIBILITY MANAGER =====
    class AccessibilityManager {
        constructor() {
            this.focusTracker = new FocusTracker();
            this.keyboardNavigator = new KeyboardNavigator();
            this.screenReaderAnnouncer = new ScreenReaderAnnouncer();
            this.contrastManager = new ContrastManager();
            this.motionManager = new MotionManager();
            this.init();
        }

        init() {
            this.setupGlobalKeyboardShortcuts();
            this.setupFocusManagement();
            this.setupFormEnhancements();
            this.setupNotificationSystem();
            this.setupProgressiveEnhancement();
            console.log('♿ WCAG AA+ Accessibility: Initialized');
        }

        setupGlobalKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Alt + 1: Skip to main content
                if (e.altKey && e.key === '1') {
                    e.preventDefault();
                    const mainContent = document.getElementById('main-content');
                    if (mainContent) {
                        mainContent.focus();
                        this.screenReaderAnnouncer.announce('Skipped to main content');
                    }
                }
                
                // Alt + 2: Skip to navigation
                if (e.altKey && e.key === '2') {
                    e.preventDefault();
                    const nav = document.querySelector('[role="navigation"]');
                    if (nav) {
                        nav.focus();
                        this.screenReaderAnnouncer.announce('Skipped to navigation');
                    }
                }
                
                // Alt + H: Toggle high contrast
                if (e.altKey && e.key === 'h') {
                    e.preventDefault();
                    this.contrastManager.toggleHighContrast();
                }
                
                // Alt + M: Toggle reduced motion
                if (e.altKey && e.key === 'm') {
                    e.preventDefault();
                    this.motionManager.toggleReducedMotion();
                }
            });
        }

        setupFocusManagement() {
            // Enhanced focus indicators
            document.addEventListener('focusin', (e) => {
                this.focusTracker.trackFocus(e.target);
            });

            // Focus trap for modals
            document.addEventListener('shown.bs.modal', (e) => {
                this.focusTracker.trapFocus(e.target);
            });

            document.addEventListener('hidden.bs.modal', (e) => {
                this.focusTracker.releaseFocus();
            });
        }

        setupFormEnhancements() {
            // Real-time validation announcements
            document.addEventListener('input', (e) => {
                if (e.target.matches('.nvc-form-control')) {
                    this.validateFieldAccessibly(e.target);
                }
            });

            // Form submission accessibility
            document.addEventListener('submit', (e) => {
                this.handleFormSubmissionAccessibly(e);
            });
        }

        validateFieldAccessibly(field) {
            const errorElement = field.parentElement.querySelector('.nvc-form-error');
            const isValid = field.checkValidity();
            
            if (!isValid && field.value.length > 0) {
                field.setAttribute('aria-invalid', 'true');
                if (errorElement) {
                    field.setAttribute('aria-describedby', errorElement.id || 'error-' + field.name);
                }
            } else {
                field.setAttribute('aria-invalid', 'false');
                field.removeAttribute('aria-describedby');
            }
        }

        handleFormSubmissionAccessibly(e) {
            const form = e.target;
            const invalidFields = form.querySelectorAll(':invalid');
            
            if (invalidFields.length > 0) {
                e.preventDefault();
                const firstInvalid = invalidFields[0];
                firstInvalid.focus();
                this.screenReaderAnnouncer.announce(
                    `Form has ${invalidFields.length} error${invalidFields.length > 1 ? 's' : ''}. Please correct and try again.`
                );
            }
        }

        setupNotificationSystem() {
            // Auto-announce notifications
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (node.matches('.nvc-notification-accessible')) {
                                this.screenReaderAnnouncer.announce(node.textContent.trim());
                            }
                        }
                    });
                });
            });

            observer.observe(document.body, { childList: true, subtree: true });
        }

        setupProgressiveEnhancement() {
            // Add accessibility features to dynamically loaded content
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.enhanceElement(node);
                        }
                    });
                });
            });

            observer.observe(document.body, { childList: true, subtree: true });
        }

        enhanceElement(element) {
            // Add WCAG focus to interactive elements
            const interactiveElements = element.querySelectorAll('button, a, input, select, textarea, [tabindex]');
            interactiveElements.forEach(el => {
                if (!el.classList.contains('nvc-wcag-focus')) {
                    el.classList.add('nvc-wcag-focus');
                }
            });

            // Ensure touch targets meet minimum size
            const touchTargets = element.querySelectorAll('button, a, input[type="checkbox"], input[type="radio"]');
            touchTargets.forEach(el => {
                if (!el.classList.contains('nvc-touch-target')) {
                    el.classList.add('nvc-touch-target');
                }
            });
        }
    }

    // ===== FOCUS TRACKER =====
    class FocusTracker {
        constructor() {
            this.focusHistory = [];
            this.trapStack = [];
        }

        trackFocus(element) {
            this.focusHistory.push(element);
            if (this.focusHistory.length > 10) {
                this.focusHistory.shift();
            }
        }

        trapFocus(container) {
            const focusableElements = container.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            
            if (focusableElements.length === 0) return;

            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            const trapHandler = (e) => {
                if (e.key === 'Tab') {
                    if (e.shiftKey) {
                        if (document.activeElement === firstElement) {
                            e.preventDefault();
                            lastElement.focus();
                        }
                    } else {
                        if (document.activeElement === lastElement) {
                            e.preventDefault();
                            firstElement.focus();
                        }
                    }
                }
            };

            container.addEventListener('keydown', trapHandler);
            this.trapStack.push({ container, handler: trapHandler });
            
            // Focus first element
            firstElement.focus();
        }

        releaseFocus() {
            const trap = this.trapStack.pop();
            if (trap) {
                trap.container.removeEventListener('keydown', trap.handler);
            }
            
            // Return focus to previous element
            if (this.focusHistory.length > 1) {
                const previousElement = this.focusHistory[this.focusHistory.length - 2];
                if (previousElement && document.contains(previousElement)) {
                    previousElement.focus();
                }
            }
        }
    }

    // ===== KEYBOARD NAVIGATOR =====
    class KeyboardNavigator {
        constructor() {
            this.setupArrowKeyNavigation();
        }

        setupArrowKeyNavigation() {
            // Arrow key navigation for card grids
            document.addEventListener('keydown', (e) => {
                if (e.target.matches('.nvc-card, .nvc-metric-card')) {
                    this.handleCardNavigation(e);
                }
            });
        }

        handleCardNavigation(e) {
            const currentCard = e.target;
            const container = currentCard.closest('.nvc-metrics-grid, .nvc-card-grid');
            if (!container) return;

            const cards = Array.from(container.querySelectorAll('.nvc-card, .nvc-metric-card'));
            const currentIndex = cards.indexOf(currentCard);
            let targetIndex;

            switch (e.key) {
                case 'ArrowRight':
                    e.preventDefault();
                    targetIndex = (currentIndex + 1) % cards.length;
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    targetIndex = (currentIndex - 1 + cards.length) % cards.length;
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    // Move to next row (approximate)
                    targetIndex = Math.min(currentIndex + 3, cards.length - 1);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    // Move to previous row (approximate)
                    targetIndex = Math.max(currentIndex - 3, 0);
                    break;
                default:
                    return;
            }

            if (targetIndex !== undefined && cards[targetIndex]) {
                cards[targetIndex].focus();
            }
        }
    }

    // ===== SCREEN READER ANNOUNCER =====
    class ScreenReaderAnnouncer {
        constructor() {
            this.createLiveRegions();
        }

        createLiveRegions() {
            // Polite announcements
            this.politeRegion = document.createElement('div');
            this.politeRegion.setAttribute('aria-live', 'polite');
            this.politeRegion.setAttribute('aria-atomic', 'true');
            this.politeRegion.className = 'nvc-sr-only';
            document.body.appendChild(this.politeRegion);

            // Assertive announcements
            this.assertiveRegion = document.createElement('div');
            this.assertiveRegion.setAttribute('aria-live', 'assertive');
            this.assertiveRegion.setAttribute('aria-atomic', 'true');
            this.assertiveRegion.className = 'nvc-sr-only';
            document.body.appendChild(this.assertiveRegion);
        }

        announce(message, priority = 'polite') {
            const region = priority === 'assertive' ? this.assertiveRegion : this.politeRegion;
            
            // Clear and set new message
            region.textContent = '';
            setTimeout(() => {
                region.textContent = message;
            }, 100);

            // Clear after announcement
            setTimeout(() => {
                region.textContent = '';
            }, 5000);
        }
    }

    // ===== CONTRAST MANAGER =====
    class ContrastManager {
        constructor() {
            this.highContrastEnabled = localStorage.getItem('nvc-high-contrast') === 'true';
            this.applyContrastPreference();
        }

        toggleHighContrast() {
            this.highContrastEnabled = !this.highContrastEnabled;
            localStorage.setItem('nvc-high-contrast', this.highContrastEnabled.toString());
            this.applyContrastPreference();
            
            const message = this.highContrastEnabled ? 'High contrast enabled' : 'High contrast disabled';
            window.accessibilityManager?.screenReaderAnnouncer.announce(message);
        }

        applyContrastPreference() {
            if (this.highContrastEnabled) {
                document.body.classList.add('nvc-high-contrast-mode');
            } else {
                document.body.classList.remove('nvc-high-contrast-mode');
            }
        }
    }

    // ===== MOTION MANAGER =====
    class MotionManager {
        constructor() {
            this.reducedMotionEnabled = localStorage.getItem('nvc-reduced-motion') === 'true' ||
                                       window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            this.applyMotionPreference();
        }

        toggleReducedMotion() {
            this.reducedMotionEnabled = !this.reducedMotionEnabled;
            localStorage.setItem('nvc-reduced-motion', this.reducedMotionEnabled.toString());
            this.applyMotionPreference();
            
            const message = this.reducedMotionEnabled ? 'Reduced motion enabled' : 'Reduced motion disabled';
            window.accessibilityManager?.screenReaderAnnouncer.announce(message);
        }

        applyMotionPreference() {
            if (this.reducedMotionEnabled) {
                document.body.classList.add('nvc-reduced-motion');
            } else {
                document.body.classList.remove('nvc-reduced-motion');
            }
        }
    }

    // ===== INITIALIZATION =====
    document.addEventListener('DOMContentLoaded', function() {
        window.accessibilityManager = new AccessibilityManager();
        
        // Add accessibility toolbar
        const toolbar = document.createElement('div');
        toolbar.className = 'nvc-accessibility-toolbar';
        toolbar.innerHTML = `
            <button type="button" class="nvc-btn nvc-btn-sm" onclick="window.accessibilityManager.contrastManager.toggleHighContrast()" title="Toggle High Contrast (Alt+H)">
                <i class="fas fa-adjust" aria-hidden="true"></i>
                <span class="nvc-sr-only">Toggle High Contrast</span>
            </button>
            <button type="button" class="nvc-btn nvc-btn-sm" onclick="window.accessibilityManager.motionManager.toggleReducedMotion()" title="Toggle Reduced Motion (Alt+M)">
                <i class="fas fa-pause" aria-hidden="true"></i>
                <span class="nvc-sr-only">Toggle Reduced Motion</span>
            </button>
        `;
        
        // Position toolbar
        toolbar.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 9999;
            background: rgba(0, 0, 0, 0.8);
            padding: 8px;
            border-radius: 4px;
            display: flex;
            gap: 4px;
        `;
        
        document.body.appendChild(toolbar);
    });

})();

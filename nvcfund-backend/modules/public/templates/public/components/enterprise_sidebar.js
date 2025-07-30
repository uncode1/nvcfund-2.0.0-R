// Legacy Enterprise Sidebar JavaScript - DISABLED
// This file is disabled to prevent conflicts with professional header navbar
class LegacyEnterpriseSidebar {
    constructor() {
        this.sidebar = document.getElementById('enterpriseSidebar');
        this.toggleBtn = document.getElementById('sidebarToggle');
        this.overlay = document.getElementById('sidebarOverlay');
        this.searchInput = document.getElementById('sidebarSearch');
        this.navItems = document.querySelectorAll('.nav-item, .nav-subitem');
        this.navGroups = document.querySelectorAll('.nav-group');
        this.isCollapsed = false;
        this.isMobile = window.innerWidth <= 768;
        
        this.init();
    }
    
    init() {
        if (!this.sidebar || !this.toggleBtn || !this.overlay) {
            console.error('Enterprise Sidebar: Required elements not found');
            return;
        }
        
        console.log('Enterprise Sidebar: Initializing...');
        
        // Initialize sidebar state
        this.initializeSidebarState();
        
        // Bind event listeners
        this.bindEvents();
        
        // Initialize navigation groups
        this.initNavigationGroups();
        
        // Initialize search functionality
        this.initSearch();
        
        // Initialize keyboard shortcuts
        this.initKeyboardShortcuts();
        
        // Set active navigation item
        this.setActiveNavItem();
        
        // Handle responsive behavior
        this.handleResize();
    }
    
    initializeSidebarState() {
        // Check localStorage for sidebar state
        const savedState = localStorage.getItem('nvc-sidebar-collapsed');
        if (savedState === 'true' && !this.isMobile) {
            this.collapse();
        } else {
            this.expand();
        }
        
        // Apply body class for content adjustment
        this.updateBodyClass();
    }
    
    bindEvents() {
        // Toggle button click
        this.toggleBtn?.addEventListener('click', () => {
            this.toggle();
        });
        
        // Overlay click (mobile)
        this.overlay?.addEventListener('click', () => {
            if (this.isMobile) {
                this.close();
            }
        });
        
        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        // Escape key to close on mobile
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isMobile && !this.isCollapsed) {
                this.close();
            }
        });
    }
    
    initNavigationGroups() {
        const groupTriggers = document.querySelectorAll('.nav-group-trigger');
        
        groupTriggers.forEach(trigger => {
            const group = trigger.closest('.nav-group');
            const content = group.querySelector('.nav-group-content');
            
            // Check if group should be expanded by default (has active item)
            const hasActiveItem = content.querySelector('.nav-subitem.active');
            if (hasActiveItem) {
                group.classList.add('expanded');
            }
            
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                if (!this.isCollapsed) {
                    this.toggleGroup(group);
                }
            });
            
            // Handle hover on collapsed state
            if (this.isCollapsed) {
                trigger.addEventListener('mouseenter', () => {
                    this.showGroupTooltip(trigger, content);
                });
                
                trigger.addEventListener('mouseleave', () => {
                    this.hideGroupTooltip();
                });
            }
        });
    }
    
    toggleGroup(group) {
        const isExpanded = group.classList.contains('expanded');
        
        // Close other groups (accordion behavior)
        const allGroups = document.querySelectorAll('.nav-group');
        allGroups.forEach(g => {
            if (g !== group) {
                g.classList.remove('expanded');
            }
        });
        
        // Toggle current group
        group.classList.toggle('expanded', !isExpanded);
        
        // Save expanded state
        const groupId = group.querySelector('.nav-group-trigger').textContent.trim();
        const expandedGroups = JSON.parse(localStorage.getItem('nvc-expanded-groups') || '[]');
        
        if (!isExpanded && !expandedGroups.includes(groupId)) {
            expandedGroups.push(groupId);
        } else if (isExpanded) {
            const index = expandedGroups.indexOf(groupId);
            if (index > -1) expandedGroups.splice(index, 1);
        }
        
        localStorage.setItem('nvc-expanded-groups', JSON.stringify(expandedGroups));
    }
    
    initSearch() {
        if (!this.searchInput) return;
        
        this.searchInput.addEventListener('input', (e) => {
            this.performSearch(e.target.value);
        });
        
        this.searchInput.addEventListener('focus', () => {
            if (this.isCollapsed && !this.isMobile) {
                this.expand();
            }
        });
    }
    
    performSearch(query) {
        const allItems = document.querySelectorAll('.nav-item, .nav-subitem');
        const groups = document.querySelectorAll('.nav-group');
        
        if (!query.trim()) {
            // Show all items
            allItems.forEach(item => {
                item.style.display = '';
            });
            groups.forEach(group => {
                group.style.display = '';
            });
            return;
        }
        
        const searchTerm = query.toLowerCase();
        let hasVisibleItems = false;
        
        // Search through navigation items
        allItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            const matches = text.includes(searchTerm);
            
            item.style.display = matches ? '' : 'none';
            if (matches) hasVisibleItems = true;
        });
        
        // Show/hide groups based on visible items
        groups.forEach(group => {
            const visibleItems = group.querySelectorAll('.nav-subitem[style=""], .nav-subitem:not([style])');
            const groupText = group.querySelector('.nav-group-trigger').textContent.toLowerCase();
            const groupMatches = groupText.includes(searchTerm);
            
            if (visibleItems.length > 0 || groupMatches) {
                group.style.display = '';
                if (visibleItems.length > 0) {
                    group.classList.add('expanded');
                }
            } else {
                group.style.display = 'none';
            }
        });
    }
    
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Cmd/Ctrl + K to focus search
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.searchInput?.focus();
            }
            
            // Cmd/Ctrl + B to toggle sidebar
            if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
                e.preventDefault();
                this.toggle();
            }
        });
    }
    
    setActiveNavItem() {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('.nav-item, .nav-subitem');
        
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href && (currentPath === href || (currentPath.startsWith(href) && href !== '/'))) {
                item.classList.add('active');
                
                // If it's a subitem, expand its parent group
                const parentGroup = item.closest('.nav-group');
                if (parentGroup) {
                    parentGroup.classList.add('expanded');
                }
            } else {
                item.classList.remove('active');
            }
        });
    }
    
    toggle() {
        if (this.isMobile) {
            this.toggleMobile();
        } else {
            this.isCollapsed ? this.expand() : this.collapse();
        }
    }
    
    collapse() {
        if (this.isMobile) return;
        
        this.isCollapsed = true;
        this.sidebar.classList.add('collapsed');
        this.updateBodyClass();
        
        // Collapse all groups
        const groups = document.querySelectorAll('.nav-group');
        groups.forEach(group => group.classList.remove('expanded'));
        
        // Save state
        localStorage.setItem('nvc-sidebar-collapsed', 'true');
        
        // Trigger custom event
        this.dispatchEvent('sidebar:collapsed');
    }
    
    expand() {
        if (this.isMobile) return;
        
        this.isCollapsed = false;
        this.sidebar.classList.remove('collapsed');
        this.updateBodyClass();
        
        // Restore expanded groups
        const expandedGroups = JSON.parse(localStorage.getItem('nvc-expanded-groups') || '[]');
        const groups = document.querySelectorAll('.nav-group');
        groups.forEach(group => {
            const groupId = group.querySelector('.nav-group-trigger').textContent.trim();
            if (expandedGroups.includes(groupId)) {
                group.classList.add('expanded');
            }
        });
        
        // Save state
        localStorage.setItem('nvc-sidebar-collapsed', 'false');
        
        // Trigger custom event
        this.dispatchEvent('sidebar:expanded');
    }
    
    toggleMobile() {
        const isOpen = this.sidebar.classList.contains('mobile-open');
        
        if (isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        if (!this.isMobile) return;
        
        this.sidebar.classList.add('mobile-open');
        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Trigger custom event
        this.dispatchEvent('sidebar:opened');
    }
    
    close() {
        if (!this.isMobile) return;
        
        this.sidebar.classList.remove('mobile-open');
        this.overlay.classList.remove('active');
        document.body.style.overflow = '';
        
        // Trigger custom event
        this.dispatchEvent('sidebar:closed');
    }
    
    updateBodyClass() {
        document.body.classList.remove('sidebar-open', 'sidebar-collapsed');
        
        if (!this.isMobile) {
            if (this.isCollapsed) {
                document.body.classList.add('sidebar-collapsed');
            } else {
                document.body.classList.add('sidebar-open');
            }
        }
    }
    
    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;
        
        if (wasMobile !== this.isMobile) {
            // Mode changed
            if (this.isMobile) {
                // Switched to mobile
                this.sidebar.classList.remove('collapsed');
                this.close();
            } else {
                // Switched to desktop
                this.sidebar.classList.remove('mobile-open');
                this.overlay.classList.remove('active');
                document.body.style.overflow = '';
                
                // Restore previous collapsed state
                const savedState = localStorage.getItem('nvc-sidebar-collapsed');
                if (savedState === 'true') {
                    this.collapse();
                } else {
                    this.expand();
                }
            }
            
            this.updateBodyClass();
        }
    }
    
    dispatchEvent(eventName) {
        const event = new CustomEvent(eventName, {
            detail: {
                isCollapsed: this.isCollapsed,
                isMobile: this.isMobile
            }
        });
        document.dispatchEvent(event);
    }
    
    // Public API methods
    getState() {
        return {
            isCollapsed: this.isCollapsed,
            isMobile: this.isMobile
        };
    }
    
    forceCollapse() {
        this.collapse();
    }
    
    forceExpand() {
        this.expand();
    }
    
    focusSearch() {
        this.searchInput?.focus();
    }
    
    showGroupTooltip(trigger, content) {
        if (!this.isCollapsed || this.isMobile) return;
        
        const tooltipText = trigger.getAttribute('data-tooltip');
        if (!tooltipText) return;
        
        // Remove existing tooltip
        this.hideGroupTooltip();
        
        // Create tooltip
        const tooltip = document.createElement('div');
        tooltip.className = 'sidebar-tooltip';
        tooltip.textContent = tooltipText;
        tooltip.style.cssText = `
            position: absolute;
            left: 100%;
            top: 50%;
            transform: translateY(-50%);
            background: var(--sidebar-bg);
            color: var(--sidebar-text);
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--sidebar-border);
            white-space: nowrap;
            margin-left: 8px;
            z-index: 1000;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            opacity: 0;
            transition: opacity 0.2s ease;
        `;
        
        trigger.style.position = 'relative';
        trigger.appendChild(tooltip);
        
        // Fade in
        setTimeout(() => {
            tooltip.style.opacity = '1';
        }, 10);
    }
    
    hideGroupTooltip() {
        const tooltip = document.querySelector('.sidebar-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
}

// Legacy sidebar initialization - DISABLED to prevent conflicts
document.addEventListener('DOMContentLoaded', () => {
    console.log('Legacy Enterprise Sidebar: DISABLED - Using professional header navbar instead');
    // Legacy initialization disabled to prevent conflicts with professional header navbar
    // window.enterpriseSidebar = new LegacyEnterpriseSidebar();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnterpriseSidebar;
}
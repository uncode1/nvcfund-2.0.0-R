/**
 * NVC Banking Platform - Interactive Dashboard JavaScript
 * Enterprise-grade real-time dashboard with comprehensive interactivity
 */

class NVCBankingDashboard {
    constructor() {
        this.isInitialized = false;
        this.charts = {};
        this.realTimeData = {};
        this.updateInterval = 30000; // 30 seconds
        this.animations = {};
        this.socketConnection = null;
        
        this.init();
    }

    init() {
        console.log('🏦 NVC Banking Dashboard: Initializing interactive features...');
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
        } else {
            this.initializeComponents();
        }
    }

    initializeComponents() {
        try {
            // Initialize core components
            this.initializeCharts();
            this.initializeRealTimeUpdates();
            this.initializeInteractiveElements();
            this.initializeNotifications();
            this.initializeSearchAndFilters();
            this.initializeKeyboardShortcuts();
            this.initializeResponsiveFeatures();
            
            this.isInitialized = true;
            console.log('✅ NVC Banking Dashboard: All interactive features initialized successfully');
            
            // Trigger initial data load
            this.loadInitialData();
            
        } catch (error) {
            console.error('❌ Dashboard initialization error:', error);
            this.showErrorNotification('Dashboard initialization failed. Some features may not work properly.');
        }
    }

    initializeCharts() {
        console.log('📊 Initializing interactive charts...');
        
        // Account Balance Trend Chart
        this.initializeBalanceTrendChart();
        
        // Transaction Volume Chart
        this.initializeTransactionVolumeChart();
        
        // Account Distribution Chart
        this.initializeAccountDistributionChart();
        
        // Performance Metrics Chart
        this.initializePerformanceMetricsChart();
    }

    initializeBalanceTrendChart() {
        const ctx = document.getElementById('balanceTrendChart');
        if (!ctx) return;

        this.charts.balanceTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateDateLabels(30),
                datasets: [{
                    label: 'Account Balance',
                    data: this.generateMockTrendData(30, 10000, 50000),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    initializeTransactionVolumeChart() {
        const ctx = document.getElementById('transactionVolumeChart');
        if (!ctx) return;

        this.charts.transactionVolume = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Transaction Volume',
                    data: [120, 95, 135, 110, 150, 80, 60],
                    backgroundColor: [
                        '#007bff', '#28a745', '#ffc107', '#dc3545', '#17a2b8', '#6f42c1', '#fd7e14'
                    ],
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    initializeAccountDistributionChart() {
        const ctx = document.getElementById('accountDistributionChart');
        if (!ctx) return;

        this.charts.accountDistribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Checking', 'Savings', 'Business', 'Investment'],
                datasets: [{
                    data: [45, 30, 15, 10],
                    backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initializePerformanceMetricsChart() {
        const ctx = document.getElementById('performanceMetricsChart');
        if (!ctx) return;

        this.charts.performanceMetrics = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Liquidity', 'Profitability', 'Efficiency', 'Growth', 'Risk Management', 'Customer Satisfaction'],
                datasets: [{
                    label: 'Current Performance',
                    data: [85, 92, 78, 88, 95, 82],
                    backgroundColor: 'rgba(0, 123, 255, 0.2)',
                    borderColor: '#007bff',
                    borderWidth: 2,
                    pointBackgroundColor: '#007bff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    initializeRealTimeUpdates() {
        console.log('🔄 Initializing real-time updates...');
        
        // Start real-time data polling
        this.startRealTimeUpdates();
        
        // Initialize WebSocket connection if available
        this.initializeWebSocket();
    }

    startRealTimeUpdates() {
        // Update key metrics every 30 seconds
        setInterval(() => {
            this.updateKeyMetrics();
            this.updateTransactionFeed();
            this.updateNotificationsBadge();
        }, this.updateInterval);
    }

    updateKeyMetrics() {
        // Simulate real-time balance updates
        const balanceElements = document.querySelectorAll('[data-metric="balance"]');
        balanceElements.forEach(element => {
            const currentValue = parseFloat(element.textContent.replace(/[$,]/g, ''));
            const change = (Math.random() - 0.5) * 1000; // Random change
            const newValue = currentValue + change;
            
            this.animateValue(element, currentValue, newValue, 1000, '$');
        });

        // Update transaction count
        const transactionElements = document.querySelectorAll('[data-metric="transactions"]');
        transactionElements.forEach(element => {
            const currentValue = parseInt(element.textContent);
            const newValue = currentValue + Math.floor(Math.random() * 3);
            this.animateValue(element, currentValue, newValue, 1000);
        });
    }

    updateTransactionFeed() {
        const feedContainer = document.getElementById('transactionFeed');
        if (!feedContainer) return;

        // Generate mock transaction
        const transaction = this.generateMockTransaction();
        const transactionElement = this.createTransactionElement(transaction);
        
        // Add to top of feed with animation
        feedContainer.insertBefore(transactionElement, feedContainer.firstChild);
        
        // Animate in
        transactionElement.style.opacity = '0';
        transactionElement.style.transform = 'translateY(-20px)';
        
        requestAnimationFrame(() => {
            transactionElement.style.transition = 'all 0.3s ease';
            transactionElement.style.opacity = '1';
            transactionElement.style.transform = 'translateY(0)';
        });
        
        // Remove old transactions to keep feed manageable
        const transactions = feedContainer.children;
        if (transactions.length > 10) {
            feedContainer.removeChild(transactions[transactions.length - 1]);
        }
    }

    initializeInteractiveElements() {
        console.log('🎯 Initializing interactive elements...');
        
        // Interactive stat cards
        this.initializeStatCards();
        
        // Dynamic action buttons
        this.initializeActionButtons();
        
        // Collapsible sections
        this.initializeCollapsibleSections();
        
        // Interactive tables
        this.initializeInteractiveTables();
        
        // Modal dialogs
        this.initializeModalDialogs();
    }

    initializeStatCards() {
        const statCards = document.querySelectorAll('.dashboard-stat-card, .stat-card');
        
        statCards.forEach(card => {
            // Add hover effects
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-5px)';
                card.style.boxShadow = '0 10px 25px rgba(0,0,0,0.2)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
            });
            
            // Add click effects
            card.addEventListener('click', () => {
                card.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    card.style.transform = 'scale(1)';
                }, 100);
            });
        });
    }

    initializeActionButtons() {
        // Quick action buttons
        const quickActionButtons = document.querySelectorAll('.quick-action-btn');
        
        quickActionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                
                const action = button.dataset.action;
                this.handleQuickAction(action);
                
                // Visual feedback
                button.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    button.style.transform = 'scale(1)';
                }, 100);
            });
        });
    }

    handleQuickAction(action) {
        console.log(`🎯 Quick action triggered: ${action}`);
        
        switch (action) {
            case 'transfer':
                this.openTransferModal();
                break;
            case 'deposit':
                this.openDepositModal();
                break;
            case 'withdraw':
                this.openWithdrawModal();
                break;
            case 'pay_bills':
                this.openBillPayModal();
                break;
            case 'view_statements':
                this.openStatementsModal();
                break;
            default:
                this.showNotification(`Action "${action}" initiated`, 'info');
        }
    }

    initializeNotifications() {
        console.log('🔔 Initializing notification system...');
        
        // Create notification container if it doesn't exist
        if (!document.getElementById('notificationContainer')) {
            const container = document.createElement('div');
            container.id = 'notificationContainer';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        
        // Initialize notification badge
        this.updateNotificationsBadge();
    }

    showNotification(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notificationContainer');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.add('notification-show');
        }, 100);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('notification-show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, duration);
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    initializeSearchAndFilters() {
        console.log('🔍 Initializing search and filters...');
        
        // Real-time search
        const searchInputs = document.querySelectorAll('.search-input');
        searchInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.handleSearch(e.target.value, e.target.dataset.searchTarget);
            });
        });
        
        // Filter controls
        const filterControls = document.querySelectorAll('.filter-control');
        filterControls.forEach(control => {
            control.addEventListener('change', (e) => {
                this.handleFilter(e.target.value, e.target.dataset.filterType);
            });
        });
    }

    handleSearch(query, target) {
        console.log(`🔍 Search: "${query}" in ${target}`);
        
        const targetElements = document.querySelectorAll(`[data-searchable="${target}"]`);
        
        targetElements.forEach(element => {
            const text = element.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            
            if (matches || query === '') {
                element.style.display = '';
                element.style.opacity = '1';
            } else {
                element.style.opacity = '0.3';
                element.style.display = 'none';
            }
        });
    }

    initializeKeyboardShortcuts() {
        console.log('⌨️ Initializing keyboard shortcuts...');
        
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + shortcuts
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'k':
                        e.preventDefault();
                        this.focusSearchInput();
                        break;
                    case 'n':
                        e.preventDefault();
                        this.openNewTransactionModal();
                        break;
                    case 'r':
                        e.preventDefault();
                        this.refreshDashboard();
                        break;
                }
            }
            
            // ESC key
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    focusSearchInput() {
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    refreshDashboard() {
        console.log('🔄 Refreshing dashboard...');
        
        // Show loading indicator
        this.showLoadingIndicator();
        
        // Simulate data refresh
        setTimeout(() => {
            this.loadInitialData();
            this.hideLoadingIndicator();
            this.showNotification('Dashboard refreshed successfully', 'success');
        }, 1000);
    }

    // Utility functions
    generateDateLabels(days) {
        const labels = [];
        for (let i = days; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        return labels;
    }

    generateMockTrendData(points, min, max) {
        const data = [];
        let current = min + (max - min) * 0.5;
        
        for (let i = 0; i < points; i++) {
            const change = (Math.random() - 0.5) * (max - min) * 0.1;
            current += change;
            current = Math.max(min, Math.min(max, current));
            data.push(Math.round(current));
        }
        
        return data;
    }

    generateMockTransaction() {
        const types = ['Deposit', 'Withdrawal', 'Transfer', 'Payment'];
        const amounts = [50, 100, 250, 500, 1000, 2500];
        const descriptions = ['Online Purchase', 'ATM Withdrawal', 'Direct Deposit', 'Bill Payment', 'Transfer'];
        
        return {
            id: Date.now(),
            type: types[Math.floor(Math.random() * types.length)],
            amount: amounts[Math.floor(Math.random() * amounts.length)],
            description: descriptions[Math.floor(Math.random() * descriptions.length)],
            time: new Date().toLocaleTimeString(),
            status: Math.random() > 0.1 ? 'completed' : 'pending'
        };
    }

    createTransactionElement(transaction) {
        const element = document.createElement('div');
        element.className = 'transaction-item';
        element.innerHTML = `
            <div class="transaction-info">
                <div class="transaction-type">${transaction.type}</div>
                <div class="transaction-description">${transaction.description}</div>
                <div class="transaction-time">${transaction.time}</div>
            </div>
            <div class="transaction-amount ${transaction.type === 'Deposit' ? 'positive' : 'negative'}">
                ${transaction.type === 'Deposit' ? '+' : '-'}$${transaction.amount}
            </div>
            <div class="transaction-status status-${transaction.status}">${transaction.status}</div>
        `;
        return element;
    }

    animateValue(element, start, end, duration, prefix = '') {
        const startTime = performance.now();
        const difference = end - start;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const current = start + (difference * this.easeInOutQuad(progress));
            
            element.textContent = prefix + Math.round(current).toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    easeInOutQuad(t) {
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    }

    loadInitialData() {
        console.log('📊 Loading initial dashboard data...');
        
        // Simulate data loading
        setTimeout(() => {
            this.updateKeyMetrics();
            this.updateChartData();
            this.showNotification('Dashboard data loaded', 'success', 3000);
        }, 500);
    }

    updateChartData() {
        // Update chart data with new information
        Object.keys(this.charts).forEach(chartKey => {
            const chart = this.charts[chartKey];
            if (chart && chart.data) {
                // Update with new data (simulate real-time updates)
                chart.update('none'); // Update without animation
            }
        });
    }

    showLoadingIndicator() {
        // Implementation for loading indicator
        console.log('⏳ Loading...');
    }

    hideLoadingIndicator() {
        // Implementation for hiding loading indicator
        console.log('✅ Loading complete');
    }

    closeAllModals() {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            if (window.bootstrap) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        });
    }

    // Modal opening methods (placeholders)
    openTransferModal() { console.log('💸 Opening transfer modal'); }
    openDepositModal() { console.log('💰 Opening deposit modal'); }
    openWithdrawModal() { console.log('🏧 Opening withdraw modal'); }
    openBillPayModal() { console.log('💳 Opening bill pay modal'); }
    openStatementsModal() { console.log('📄 Opening statements modal'); }
    openNewTransactionModal() { console.log('📝 Opening new transaction modal'); }

    // Additional interactive features
    initializeCollapsibleSections() {
        const collapsibles = document.querySelectorAll('[data-toggle="collapse"]');
        collapsibles.forEach(element => {
            element.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = element.dataset.target;
                const target = document.querySelector(targetId);
                
                if (target) {
                    if (target.classList.contains('show')) {
                        target.classList.remove('show');
                        element.classList.add('collapsed');
                    } else {
                        target.classList.add('show');
                        element.classList.remove('collapsed');
                    }
                }
            });
        });
    }

    initializeInteractiveTables() {
        const tables = document.querySelectorAll('.interactive-table');
        tables.forEach(table => {
            // Add sorting functionality
            const headers = table.querySelectorAll('th[data-sort]');
            headers.forEach(header => {
                header.addEventListener('click', () => {
                    const column = header.dataset.sort;
                    this.sortTable(table, column);
                });
            });
        });
    }

    sortTable(table, column) {
        console.log(`🔤 Sorting table by ${column}`);
        // Table sorting implementation
    }

    initializeModalDialogs() {
        // Modal dialog enhancements
        const modalTriggers = document.querySelectorAll('[data-modal-trigger]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modalTrigger;
                const modal = document.getElementById(modalId);
                
                if (modal && window.bootstrap) {
                    const modalInstance = new bootstrap.Modal(modal);
                    modalInstance.show();
                }
            });
        });
    }

    initializeWebSocket() {
        // WebSocket connection for real-time updates
        if (typeof io !== 'undefined') {
            try {
                this.socketConnection = io('/dashboard');
                
                this.socketConnection.on('connect', () => {
                    console.log('🔗 WebSocket connected for real-time updates');
                });
                
                this.socketConnection.on('balance_update', (data) => {
                    this.handleBalanceUpdate(data);
                });
                
                this.socketConnection.on('transaction_update', (data) => {
                    this.handleTransactionUpdate(data);
                });
                
            } catch (error) {
                console.log('WebSocket not available, using polling updates');
            }
        }
    }

    handleBalanceUpdate(data) {
        // Handle real-time balance updates
        console.log('💰 Balance update received:', data);
    }

    handleTransactionUpdate(data) {
        // Handle real-time transaction updates
        console.log('💳 Transaction update received:', data);
    }

    updateNotificationsBadge() {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            // Simulate notification count
            const count = Math.floor(Math.random() * 5) + 1;
            badge.textContent = count;
            badge.style.display = count > 0 ? 'block' : 'none';
        }
    }

    initializeResponsiveFeatures() {
        // Add responsive behavior
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    handleResize() {
        // Handle responsive chart resizing
        Object.keys(this.charts).forEach(chartKey => {
            const chart = this.charts[chartKey];
            if (chart) {
                chart.resize();
            }
        });
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.nvcDashboard = new NVCBankingDashboard();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NVCBankingDashboard;
}
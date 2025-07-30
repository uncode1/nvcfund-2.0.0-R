/**
 * World-Class Fintech UI Interactions
 * NVC Banking Platform - Premium User Experience
 * Version: 4.0.0 - Advanced Interactions & Animations
 */

(function() {
    'use strict';

    // ===== WORLD-CLASS CARD INTERACTIONS =====
    class WorldClassCardManager {
        constructor() {
            this.init();
        }

        init() {
            this.setupCardHoverEffects();
            this.setupClickableCards();
            this.setupMetricAnimations();
            this.setupChartInteractions();
            this.setupDrillDownFunctionality();
            console.log('🎨 World-Class UI: Card interactions initialized');
        }

        setupCardHoverEffects() {
            // Enhanced hover effects for premium cards
            document.querySelectorAll('.nvc-card-premium, .nvc-metric-card').forEach(card => {
                card.addEventListener('mouseenter', (e) => {
                    this.animateCardHover(e.target, true);
                });

                card.addEventListener('mouseleave', (e) => {
                    this.animateCardHover(e.target, false);
                });
            });
        }

        animateCardHover(card, isHovering) {
            const icon = card.querySelector('.nvc-metric-icon');
            const value = card.querySelector('.nvc-metric-value');
            
            if (isHovering) {
                // Add glow effect
                card.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(37, 99, 235, 0.1)';
                
                // Animate icon
                if (icon) {
                    icon.style.transform = 'scale(1.1) rotate(5deg)';
                    icon.style.boxShadow = '0 8px 16px rgba(37, 99, 235, 0.3)';
                }
                
                // Animate value
                if (value) {
                    value.style.color = '#2563eb'; // finra-primary
                }
            } else {
                // Reset styles
                card.style.boxShadow = '';
                
                if (icon) {
                    icon.style.transform = '';
                    icon.style.boxShadow = '';
                }
                
                if (value) {
                    value.style.color = '';
                }
            }
        }

        setupClickableCards() {
            document.querySelectorAll('[data-href]').forEach(card => {
                card.addEventListener('click', (e) => {
                    const href = card.dataset.href;
                    if (href) {
                        // Add click animation
                        card.style.transform = 'translateY(-2px) scale(0.98)';
                        
                        setTimeout(() => {
                            window.location.href = href;
                        }, 150);
                    }
                });

                // Keyboard support
                card.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        card.click();
                    }
                });
            });
        }

        setupMetricAnimations() {
            // Animate metric values on scroll
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateMetricValue(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            document.querySelectorAll('.nvc-metric-value').forEach(metric => {
                observer.observe(metric);
            });
        }

        animateMetricValue(element) {
            const finalValue = element.textContent.trim();
            const numericValue = parseFloat(finalValue.replace(/[^0-9.-]/g, ''));
            
            if (!isNaN(numericValue)) {
                let currentValue = 0;
                const increment = numericValue / 60; // 60 frames for 1 second
                const prefix = finalValue.match(/^[^0-9]*/)[0];
                const suffix = finalValue.match(/[^0-9]*$/)[0];
                
                const animate = () => {
                    currentValue += increment;
                    if (currentValue < numericValue) {
                        element.textContent = prefix + Math.floor(currentValue).toLocaleString() + suffix;
                        requestAnimationFrame(animate);
                    } else {
                        element.textContent = finalValue;
                    }
                };
                
                animate();
            }
        }

        setupChartInteractions() {
            // Chart interaction handlers
            window.refreshChart = (chartId) => {
                const chartContainer = document.getElementById(chartId);
                if (chartContainer) {
                    this.showChartLoading(chartContainer);
                    
                    // Simulate data refresh
                    setTimeout(() => {
                        this.hideChartLoading(chartContainer);
                        this.announceToScreenReader('Chart data refreshed');
                    }, 1500);
                }
            };

            window.exportChart = (chartId) => {
                const chartContainer = document.getElementById(chartId);
                if (chartContainer) {
                    const canvas = chartContainer.querySelector('canvas');
                    if (canvas) {
                        // Create download link
                        const link = document.createElement('a');
                        link.download = `chart-${chartId}-${new Date().toISOString().split('T')[0]}.png`;
                        link.href = canvas.toDataURL();
                        link.click();
                        
                        this.announceToScreenReader('Chart exported successfully');
                    }
                }
            };

            window.fullscreenChart = (chartId) => {
                const chartContainer = document.getElementById(chartId);
                if (chartContainer) {
                    if (chartContainer.requestFullscreen) {
                        chartContainer.requestFullscreen();
                    }
                }
            };
        }

        setupDrillDownFunctionality() {
            window.drillDown = (itemId) => {
                // Create drill-down modal or navigate to detail view
                const modal = this.createDrillDownModal(itemId);
                document.body.appendChild(modal);
                
                // Show modal with animation
                setTimeout(() => {
                    modal.classList.add('show');
                }, 10);
                
                this.announceToScreenReader(`Viewing details for item ${itemId}`);
            };
        }

        createDrillDownModal(itemId) {
            const modal = document.createElement('div');
            modal.className = 'nvc-drill-down-modal';
            modal.innerHTML = `
                <div class="nvc-modal-backdrop" onclick="this.parentElement.remove()"></div>
                <div class="nvc-modal-content">
                    <div class="nvc-modal-header">
                        <h3>Item Details: ${itemId}</h3>
                        <button type="button" class="nvc-modal-close" onclick="this.closest('.nvc-drill-down-modal').remove()" aria-label="Close modal">
                            <i class="fas fa-times" aria-hidden="true"></i>
                        </button>
                    </div>
                    <div class="nvc-modal-body">
                        <div class="nvc-loading-accessible" aria-busy="true">
                            Loading detailed information...
                        </div>
                    </div>
                </div>
            `;
            
            return modal;
        }

        showChartLoading(container) {
            const loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'nvc-chart-loading-overlay';
            loadingOverlay.innerHTML = `
                <div class="nvc-loading-spinner"></div>
                <p>Refreshing chart data...</p>
            `;
            container.appendChild(loadingOverlay);
        }

        hideChartLoading(container) {
            const overlay = container.querySelector('.nvc-chart-loading-overlay');
            if (overlay) {
                overlay.remove();
            }
        }

        announceToScreenReader(message) {
            if (window.accessibilityManager?.screenReaderAnnouncer) {
                window.accessibilityManager.screenReaderAnnouncer.announce(message);
            }
        }
    }

    // ===== ADVANCED DATA VISUALIZATION =====
    class DataVisualizationManager {
        constructor() {
            this.charts = new Map();
            this.init();
        }

        init() {
            this.setupSparklines();
            this.setupProgressBars();
            this.setupMiniCharts();
            console.log('📊 Data Visualization: Advanced charts initialized');
        }

        setupSparklines() {
            document.querySelectorAll('.nvc-mini-chart[data-values]').forEach(element => {
                const values = element.dataset.values.split(',').map(Number);
                this.renderSparkline(element, values);
            });
        }

        renderSparkline(element, values) {
            const canvas = document.createElement('canvas');
            canvas.width = element.offsetWidth * 2; // High DPI
            canvas.height = element.offsetHeight * 2;
            canvas.style.width = '100%';
            canvas.style.height = '100%';
            
            const ctx = canvas.getContext('2d');
            ctx.scale(2, 2); // High DPI scaling
            
            const width = element.offsetWidth;
            const height = element.offsetHeight;
            const max = Math.max(...values);
            const min = Math.min(...values);
            const range = max - min || 1;
            
            // Draw sparkline
            ctx.strokeStyle = '#2563eb';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            values.forEach((value, index) => {
                const x = (index / (values.length - 1)) * width;
                const y = height - ((value - min) / range) * height;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
            
            // Add gradient fill
            ctx.globalAlpha = 0.3;
            ctx.fillStyle = '#2563eb';
            ctx.lineTo(width, height);
            ctx.lineTo(0, height);
            ctx.closePath();
            ctx.fill();
            
            element.appendChild(canvas);
        }

        setupProgressBars() {
            document.querySelectorAll('.nvc-progress-bar[data-progress]').forEach(bar => {
                const progress = parseInt(bar.dataset.progress);
                this.animateProgressBar(bar, progress);
            });
        }

        animateProgressBar(bar, targetProgress) {
            let currentProgress = 0;
            const increment = targetProgress / 60; // 60 frames
            
            const animate = () => {
                currentProgress += increment;
                if (currentProgress < targetProgress) {
                    bar.style.width = `${currentProgress}%`;
                    requestAnimationFrame(animate);
                } else {
                    bar.style.width = `${targetProgress}%`;
                }
            };
            
            // Start animation after a short delay
            setTimeout(animate, 500);
        }

        setupMiniCharts() {
            // Initialize any Chart.js instances for mini charts
            document.querySelectorAll('canvas[id^="chart-canvas-"]').forEach(canvas => {
                if (window.Chart) {
                    this.initializeChart(canvas);
                }
            });
        }

        initializeChart(canvas) {
            const ctx = canvas.getContext('2d');
            
            // Sample chart configuration
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Performance',
                        data: [12, 19, 3, 5, 2, 3],
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
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
                        x: {
                            display: false
                        },
                        y: {
                            display: false
                        }
                    }
                }
            });
            
            this.charts.set(canvas.id, chart);
        }
    }

    // ===== INITIALIZATION =====
    document.addEventListener('DOMContentLoaded', function() {
        window.worldClassCardManager = new WorldClassCardManager();
        window.dataVisualizationManager = new DataVisualizationManager();
        
        // Global utility functions
        window.toggleTableFilter = function() {
            const filters = document.querySelector('.nvc-table-filters');
            if (filters) {
                filters.style.display = filters.style.display === 'none' ? 'block' : 'none';
            }
        };
        
        window.exportTableData = function() {
            // Export table data as CSV
            const table = document.querySelector('.nvc-table-premium');
            if (table) {
                const csv = Array.from(table.querySelectorAll('tr'))
                    .map(row => Array.from(row.querySelectorAll('th, td'))
                        .map(cell => cell.textContent.trim())
                        .join(','))
                    .join('\n');
                
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `table-data-${new Date().toISOString().split('T')[0]}.csv`;
                link.click();
                URL.revokeObjectURL(url);
            }
        };
        
        window.sortTable = function(header) {
            // Table sorting functionality
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(header.parentElement.children).indexOf(header);
            const currentSort = header.getAttribute('aria-sort');
            
            // Reset all headers
            table.querySelectorAll('th[aria-sort]').forEach(th => {
                th.setAttribute('aria-sort', 'none');
                th.classList.remove('nvc-sort-asc', 'nvc-sort-desc');
            });
            
            // Determine new sort direction
            const newSort = currentSort === 'ascending' ? 'descending' : 'ascending';
            header.setAttribute('aria-sort', newSort);
            header.classList.add(newSort === 'ascending' ? 'nvc-sort-asc' : 'nvc-sort-desc');
            
            // Sort rows
            rows.sort((a, b) => {
                const aText = a.children[columnIndex].textContent.trim();
                const bText = b.children[columnIndex].textContent.trim();
                
                // Try numeric comparison first
                const aNum = parseFloat(aText.replace(/[^0-9.-]/g, ''));
                const bNum = parseFloat(bText.replace(/[^0-9.-]/g, ''));
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return newSort === 'ascending' ? aNum - bNum : bNum - aNum;
                }
                
                // Fallback to string comparison
                return newSort === 'ascending' 
                    ? aText.localeCompare(bText)
                    : bText.localeCompare(aText);
            });
            
            // Re-append sorted rows
            rows.forEach(row => tbody.appendChild(row));
        };
    });

})();

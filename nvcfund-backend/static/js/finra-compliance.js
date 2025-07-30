/**
 * FINRA Compliance JavaScript
 * NVC Banking Platform - Regulatory Compliance
 * Version: 3.0.0 - FINRA Rule 4511 Compliant
 */

(function() {
    'use strict';

    // ===== FINRA TABLE FUNCTIONALITY =====
    class FINRATable {
        constructor(tableElement) {
            this.table = tableElement;
            this.tableId = tableElement.id;
            this.announcements = document.getElementById(`${this.tableId}-announcements`);
            this.init();
        }

        init() {
            this.setupSorting();
            this.setupAuditTrail();
            this.setupExport();
            this.setupAccessibility();
            this.logAuditEvent('table_initialized');
        }

        setupSorting() {
            const sortableHeaders = this.table.querySelectorAll('.nvc-sortable');
            
            sortableHeaders.forEach(header => {
                header.addEventListener('click', (e) => this.handleSort(e));
                header.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        this.handleSort(e);
                    }
                });
            });
        }

        handleSort(event) {
            const header = event.currentTarget;
            const sortField = header.dataset.sort;
            const currentSort = header.getAttribute('aria-sort');
            
            // Reset all other headers
            this.table.querySelectorAll('.nvc-sortable').forEach(h => {
                if (h !== header) {
                    h.setAttribute('aria-sort', 'none');
                    h.classList.remove('nvc-sort-asc', 'nvc-sort-desc');
                }
            });

            // Toggle current header
            let newSort;
            if (currentSort === 'ascending') {
                newSort = 'descending';
                header.classList.remove('nvc-sort-asc');
                header.classList.add('nvc-sort-desc');
            } else {
                newSort = 'ascending';
                header.classList.remove('nvc-sort-desc');
                header.classList.add('nvc-sort-asc');
            }
            
            header.setAttribute('aria-sort', newSort);
            
            // Perform sort
            this.sortTable(sortField, newSort === 'ascending');
            
            // Announce to screen readers
            this.announce(`Table sorted by ${header.textContent.trim()} in ${newSort} order`);
            
            // Log audit event
            this.logAuditEvent('table_sorted', { field: sortField, direction: newSort });
        }

        sortTable(field, ascending) {
            const tbody = this.table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort((a, b) => {
                let aVal, bVal;
                
                if (field === 'amount') {
                    aVal = parseFloat(a.querySelector(`[data-sort-value]`)?.dataset.sortValue || 0);
                    bVal = parseFloat(b.querySelector(`[data-sort-value]`)?.dataset.sortValue || 0);
                } else if (field === 'timestamp') {
                    aVal = new Date(a.querySelector('time')?.getAttribute('datetime') || 0);
                    bVal = new Date(b.querySelector('time')?.getAttribute('datetime') || 0);
                } else {
                    const aCell = a.querySelector(`.nvc-col-${field}`);
                    const bCell = b.querySelector(`.nvc-col-${field}`);
                    aVal = aCell?.textContent.trim().toLowerCase() || '';
                    bVal = bCell?.textContent.trim().toLowerCase() || '';
                }
                
                if (aVal < bVal) return ascending ? -1 : 1;
                if (aVal > bVal) return ascending ? 1 : -1;
                return 0;
            });
            
            // Re-append sorted rows
            rows.forEach(row => tbody.appendChild(row));
        }

        setupAuditTrail() {
            const auditButtons = this.table.querySelectorAll('[data-audit-transaction]');
            
            auditButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const transactionId = e.currentTarget.dataset.auditTransaction;
                    this.showAuditTrail(transactionId);
                });
            });
        }

        async showAuditTrail(transactionId) {
            try {
                // Show modal
                const modal = document.getElementById(`auditModal-${transactionId}`);
                if (modal) {
                    const bsModal = new bootstrap.Modal(modal);
                    bsModal.show();
                    
                    // Load audit trail data
                    const content = modal.querySelector(`#auditContent-${transactionId}`);
                    content.innerHTML = '<div class="nvc-loading-accessible" aria-busy="true">Loading audit trail...</div>';
                    
                    const response = await fetch(`/api/audit-trail/${transactionId}`);
                    const auditData = await response.json();
                    
                    content.innerHTML = this.renderAuditTrail(auditData);
                    content.setAttribute('aria-busy', 'false');
                    
                    // Log audit access
                    this.logAuditEvent('audit_trail_accessed', { transaction_id: transactionId });
                }
            } catch (error) {
                console.error('Failed to load audit trail:', error);
                this.announce('Failed to load audit trail. Please try again.');
            }
        }

        renderAuditTrail(auditData) {
            return `
                <div class="nvc-audit-trail">
                    <div class="nvc-audit-summary">
                        <h4>Transaction Summary</h4>
                        <dl class="nvc-audit-details">
                            <dt>Transaction ID:</dt>
                            <dd>${auditData.transaction_id}</dd>
                            <dt>Created:</dt>
                            <dd>${new Date(auditData.created_at).toLocaleString()}</dd>
                            <dt>Status:</dt>
                            <dd><span class="nvc-status-badge nvc-status-${auditData.status}">${auditData.status}</span></dd>
                        </dl>
                    </div>
                    <div class="nvc-audit-events">
                        <h4>Audit Events</h4>
                        <div class="nvc-audit-timeline">
                            ${auditData.events.map(event => `
                                <div class="nvc-audit-event">
                                    <div class="nvc-audit-timestamp">${new Date(event.timestamp).toLocaleString()}</div>
                                    <div class="nvc-audit-user">${event.user}</div>
                                    <div class="nvc-audit-action">${event.action}</div>
                                    <div class="nvc-audit-details">${event.details || ''}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        }

        setupExport() {
            // Export functionality will be handled by global export functions
            // This method can be extended for table-specific export logic
        }

        setupAccessibility() {
            // Ensure table has proper ARIA labels
            if (!this.table.getAttribute('aria-label')) {
                this.table.setAttribute('aria-label', 'FINRA-compliant transaction table');
            }
            
            // Setup keyboard navigation for table cells
            this.setupKeyboardNavigation();
        }

        setupKeyboardNavigation() {
            const cells = this.table.querySelectorAll('td, th');
            
            cells.forEach((cell, index) => {
                cell.addEventListener('keydown', (e) => {
                    let targetIndex;
                    const currentRow = cell.parentElement;
                    const currentCellIndex = Array.from(currentRow.children).indexOf(cell);
                    
                    switch (e.key) {
                        case 'ArrowRight':
                            e.preventDefault();
                            targetIndex = index + 1;
                            break;
                        case 'ArrowLeft':
                            e.preventDefault();
                            targetIndex = index - 1;
                            break;
                        case 'ArrowDown':
                            e.preventDefault();
                            const nextRow = currentRow.nextElementSibling;
                            if (nextRow) {
                                const targetCell = nextRow.children[currentCellIndex];
                                if (targetCell) targetCell.focus();
                            }
                            return;
                        case 'ArrowUp':
                            e.preventDefault();
                            const prevRow = currentRow.previousElementSibling;
                            if (prevRow) {
                                const targetCell = prevRow.children[currentCellIndex];
                                if (targetCell) targetCell.focus();
                            }
                            return;
                    }
                    
                    if (targetIndex >= 0 && targetIndex < cells.length) {
                        cells[targetIndex].focus();
                    }
                });
            });
        }

        announce(message) {
            if (this.announcements) {
                this.announcements.textContent = message;
                // Clear after 5 seconds
                setTimeout(() => {
                    this.announcements.textContent = '';
                }, 5000);
            }
        }

        logAuditEvent(action, details = {}) {
            const auditData = {
                timestamp: new Date().toISOString(),
                table_id: this.tableId,
                action: action,
                user: window.currentUser?.username || 'anonymous',
                session_id: window.sessionId || 'unknown',
                details: details
            };
            
            // Use the global interaction manager for logging
            window.NVCInteractionManager?.sendLog('audit', auditData);
        }
    }

    // ===== GLOBAL EXPORT FUNCTIONS =====
    window.exportTable = function(tableId, format) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const finraTable = table.finraInstance;
        if (finraTable) {
            finraTable.logAuditEvent('table_exported', { format: format });
        }
        
        // Create export URL with FINRA compliance metadata
        const exportUrl = `/api/export/${tableId}?format=${format}&compliance=finra&session=${window.sessionId}`;
        
        // Trigger download
        const link = document.createElement('a');
        link.href = exportUrl;
        link.download = `finra-transactions-${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    window.exportAuditTrail = function(transactionId) {
        const exportUrl = `/api/export/audit-trail/${transactionId}?format=pdf&compliance=finra`;
        
        const link = document.createElement('a');
        link.href = exportUrl;
        link.download = `audit-trail-${transactionId}-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // ===== INITIALIZATION =====
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize all FINRA tables
        const finraTables = document.querySelectorAll('.nvc-finra-table[data-finra-compliant="true"]');
        
        finraTables.forEach(table => {
            table.finraInstance = new FINRATable(table);
        });
        
        console.log(`🏦 FINRA Compliance: Initialized ${finraTables.length} compliant tables`);
    });

})();

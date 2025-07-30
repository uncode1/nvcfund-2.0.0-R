
"""
Dashboard Widgets - Modular Dashboard Components
Provides reusable widgets and components for dashboards
"""

from flask import render_template_string
from datetime import datetime
import json

class DashboardWidget:
    """Base class for dashboard widgets"""
    
    def __init__(self, widget_id, title, widget_type='generic'):
        self.widget_id = widget_id
        self.title = title
        self.widget_type = widget_type
        self.data = {}
        self.config = {}
    
    def render(self):
        """Render the widget HTML"""
        return f"<div id='{self.widget_id}' class='dashboard-widget {self.widget_type}'><h3>{self.title}</h3></div>"
    
    def get_data(self):
        """Get widget data"""
        return self.data
    
    def update_data(self, new_data):
        """Update widget data"""
        self.data.update(new_data)

class AccountSummaryWidget(DashboardWidget):
    """Account summary widget"""
    
    def __init__(self):
        super().__init__('account-summary', 'Account Summary', 'account-summary')
        self.data = {
            'checking': '$0.00',
            'savings': '$0.00',
            'investment': '$0.00'
        }
    
    def render(self):
        template = """
        <div id="{{ widget_id }}" class="dashboard-widget account-summary-widget">
            <div class="widget-header">
                <h3>{{ title }}</h3>
                <i class="fas fa-university"></i>
            </div>
            <div class="widget-content">
                <div class="account-item">
                    <span class="account-type">Checking</span>
                    <span class="account-balance">{{ data.checking }}</span>
                </div>
                <div class="account-item">
                    <span class="account-type">Savings</span>
                    <span class="account-balance">{{ data.savings }}</span>
                </div>
                <div class="account-item">
                    <span class="account-type">Investment</span>
                    <span class="account-balance">{{ data.investment }}</span>
                </div>
            </div>
        </div>
        """
        return render_template_string(template, 
                                    widget_id=self.widget_id,
                                    title=self.title,
                                    data=self.data)

class RecentTransactionsWidget(DashboardWidget):
    """Recent transactions widget"""
    
    def __init__(self):
        super().__init__('recent-transactions', 'Recent Transactions', 'transactions')
        self.data = {'transactions': []}
    
    def render(self):
        template = """
        <div id="{{ widget_id }}" class="dashboard-widget transactions-widget">
            <div class="widget-header">
                <h3>{{ title }}</h3>
                <i class="fas fa-exchange-alt"></i>
            </div>
            <div class="widget-content">
                {% if data.transactions %}
                    {% for transaction in data.transactions %}
                    <div class="transaction-item">
                        <div class="transaction-type">
                            <i class="fas fa-{{ 'arrow-up' if transaction.type == 'transfer' else 'arrow-down' }}"></i>
                            {{ transaction.description }}
                        </div>
                        <div class="transaction-details">
                            <span class="transaction-amount">{{ transaction.get('amount', '') }}</span>
                            <span class="transaction-time">{{ transaction.timestamp }}</span>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="no-transactions">No recent transactions</p>
                {% endif %}
            </div>
        </div>
        """
        return render_template_string(template,
                                    widget_id=self.widget_id,
                                    title=self.title,
                                    data=self.data)

class QuickActionsWidget(DashboardWidget):
    """Quick actions widget"""
    
    def __init__(self):
        super().__init__('quick-actions', 'Quick Actions', 'quick-actions')
        self.data = {'actions': []}
    
    def render(self):
        template = """
        <div id="{{ widget_id }}" class="dashboard-widget quick-actions-widget">
            <div class="widget-header">
                <h3>{{ title }}</h3>
                <i class="fas fa-bolt"></i>
            </div>
            <div class="widget-content">
                <div class="actions-grid">
                    {% for action in data.actions %}
                    <a href="{{ action.route }}" class="action-button">
                        <i class="{{ action.icon }}"></i>
                        <span>{{ action.title }}</span>
                    </a>
                    {% endfor %}
                </div>
            </div>
        </div>
        """
        return render_template_string(template,
                                    widget_id=self.widget_id,
                                    title=self.title,
                                    data=self.data)

class SystemHealthWidget(DashboardWidget):
    """System health widget for admin dashboards"""
    
    def __init__(self):
        super().__init__('system-health', 'System Health', 'system-health')
        self.data = {
            'status': 'operational',
            'uptime': '99.9%',
            'active_sessions': 0,
            'database_status': 'connected'
        }
    
    def render(self):
        template = """
        <div id="{{ widget_id }}" class="dashboard-widget system-health-widget">
            <div class="widget-header">
                <h3>{{ title }}</h3>
                <i class="fas fa-heartbeat"></i>
            </div>
            <div class="widget-content">
                <div class="health-metrics">
                    <div class="metric">
                        <span class="metric-label">Status</span>
                        <span class="metric-value status-{{ data.status }}">{{ data.status.title() }}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Uptime</span>
                        <span class="metric-value">{{ data.uptime }}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Active Sessions</span>
                        <span class="metric-value">{{ data.active_sessions }}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Database</span>
                        <span class="metric-value status-{{ data.database_status }}">{{ data.database_status.title() }}</span>
                    </div>
                </div>
            </div>
        </div>
        """
        return render_template_string(template,
                                    widget_id=self.widget_id,
                                    title=self.title,
                                    data=self.data)

class TreasuryMetricsWidget(DashboardWidget):
    """Treasury metrics widget"""
    
    def __init__(self):
        super().__init__('treasury-metrics', 'Treasury Metrics', 'treasury-metrics')
        self.data = {
            'nvct_supply': '30T NVCT',
            'asset_backing': '$56.7T',
            'collateral_ratio': '189%',
            'liquidity_pool': '$1.8B'
        }
    
    def render(self):
        template = """
        <div id="{{ widget_id }}" class="dashboard-widget treasury-metrics-widget">
            <div class="widget-header">
                <h3>{{ title }}</h3>
                <i class="fas fa-coins"></i>
            </div>
            <div class="widget-content">
                <div class="treasury-grid">
                    <div class="treasury-item">
                        <span class="treasury-label">NVCT Supply</span>
                        <span class="treasury-value">{{ data.nvct_supply }}</span>
                    </div>
                    <div class="treasury-item">
                        <span class="treasury-label">Asset Backing</span>
                        <span class="treasury-value">{{ data.asset_backing }}</span>
                    </div>
                    <div class="treasury-item">
                        <span class="treasury-label">Collateral Ratio</span>
                        <span class="treasury-value">{{ data.collateral_ratio }}</span>
                    </div>
                    <div class="treasury-item">
                        <span class="treasury-label">Liquidity Pool</span>
                        <span class="treasury-value">{{ data.liquidity_pool }}</span>
                    </div>
                </div>
            </div>
        </div>
        """
        return render_template_string(template,
                                    widget_id=self.widget_id,
                                    title=self.title,
                                    data=self.data)

class WidgetFactory:
    """Factory for creating dashboard widgets"""
    
    @staticmethod
    def create_widget(widget_type, **kwargs):
        """Create a widget based on type"""
        widgets = {
            'account_summary': AccountSummaryWidget,
            'recent_transactions': RecentTransactionsWidget,
            'quick_actions': QuickActionsWidget,
            'system_health': SystemHealthWidget,
            'treasury_metrics': TreasuryMetricsWidget
        }
        
        widget_class = widgets.get(widget_type)
        if widget_class:
            widget = widget_class()
            if kwargs:
                widget.update_data(kwargs)
            return widget
        return None
    
    @staticmethod
    def create_dashboard_layout(user_role):
        """Create default widget layout for user role"""
        layouts = {
            'admin': ['system_health', 'recent_transactions', 'quick_actions'],
            'treasury_officer': ['treasury_metrics', 'recent_transactions', 'quick_actions'],
            'standard': ['account_summary', 'recent_transactions', 'quick_actions']
        }
        
        layout = layouts.get(user_role.lower(), layouts['standard'])
        widgets = []
        
        for widget_type in layout:
            widget = WidgetFactory.create_widget(widget_type)
            if widget:
                widgets.append(widget)
        
        return widgets

class DashboardRenderer:
    """Main dashboard renderer using widgets"""
    
    def __init__(self):
        self.widgets = []
    
    def add_widget(self, widget):
        """Add a widget to the dashboard"""
        self.widgets.append(widget)
    
    def render_dashboard(self, layout_class='dashboard-grid'):
        """Render complete dashboard with all widgets"""
        widget_html = []
        for widget in self.widgets:
            widget_html.append(widget.render())
        
        template = f"""
        <div class="{layout_class}">
            {''.join(widget_html)}
        </div>
        """
        return template
    
    def get_dashboard_data(self):
        """Get all widget data as JSON"""
        data = {}
        for widget in self.widgets:
            data[widget.widget_id] = widget.get_data()
        return json.dumps(data)

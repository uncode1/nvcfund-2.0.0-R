"""
Performance Monitoring Dashboard for NVC Banking Platform
Real-time performance metrics and optimization recommendations
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque, defaultdict
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from modules.core.security_decorators import require_role
from modules.core.performance import perf_monitor
from modules.core.caching_strategy import cache, CacheMaintenance
from modules.core.database_optimization import ConnectionPoolOptimizer
from modules.core.extensions import db
import logging

logger = logging.getLogger(__name__)

performance_bp = Blueprint('performance', __name__, url_prefix='/admin/performance')

class PerformanceCollector:
    """Collects and stores performance metrics"""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.metrics = {
            'response_times': deque(maxlen=max_samples),
            'query_counts': deque(maxlen=max_samples),
            'cache_hit_rates': deque(maxlen=max_samples),
            'memory_usage': deque(maxlen=max_samples),
            'cpu_usage': deque(maxlen=max_samples),
            'active_connections': deque(maxlen=max_samples),
            'error_rates': deque(maxlen=max_samples)
        }
        self.slow_queries = deque(maxlen=100)
        self.error_log = deque(maxlen=100)
        self.alerts = deque(maxlen=50)
        self.lock = threading.Lock()
        
        # Start background collection
        self.collection_thread = threading.Thread(target=self._collect_system_metrics, daemon=True)
        self.collection_thread.start()
    
    def add_request_metric(self, response_time: float, query_count: int, cache_hit_rate: float, error: bool = False):
        """Add request-level metrics"""
        with self.lock:
            timestamp = datetime.utcnow()
            
            self.metrics['response_times'].append({
                'timestamp': timestamp,
                'value': response_time
            })
            
            self.metrics['query_counts'].append({
                'timestamp': timestamp,
                'value': query_count
            })
            
            self.metrics['cache_hit_rates'].append({
                'timestamp': timestamp,
                'value': cache_hit_rate
            })
            
            self.metrics['error_rates'].append({
                'timestamp': timestamp,
                'value': 1 if error else 0
            })
            
            # Check for performance alerts
            self._check_alerts(response_time, query_count, cache_hit_rate)
    
    def add_slow_query(self, query: str, duration: float, timestamp: datetime = None):
        """Add slow query information"""
        with self.lock:
            self.slow_queries.append({
                'timestamp': timestamp or datetime.utcnow(),
                'query': query[:500] + '...' if len(query) > 500 else query,
                'duration': duration
            })
    
    def add_error(self, error_type: str, message: str, timestamp: datetime = None):
        """Add error information"""
        with self.lock:
            self.error_log.append({
                'timestamp': timestamp or datetime.utcnow(),
                'type': error_type,
                'message': message
            })
    
    def _collect_system_metrics(self):
        """Background thread to collect system metrics"""
        while True:
            try:
                timestamp = datetime.utcnow()
                
                # System metrics
                memory_percent = psutil.virtual_memory().percent
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Database connection metrics
                db_stats = ConnectionPoolOptimizer.monitor_connection_usage()
                active_connections = db_stats.get('checked_out', 0)
                
                with self.lock:
                    self.metrics['memory_usage'].append({
                        'timestamp': timestamp,
                        'value': memory_percent
                    })
                    
                    self.metrics['cpu_usage'].append({
                        'timestamp': timestamp,
                        'value': cpu_percent
                    })
                    
                    self.metrics['active_connections'].append({
                        'timestamp': timestamp,
                        'value': active_connections
                    })
                
                # Check system alerts
                self._check_system_alerts(memory_percent, cpu_percent, active_connections)
                
                time.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                logger.error(f"System metrics collection error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _check_alerts(self, response_time: float, query_count: int, cache_hit_rate: float):
        """Check for performance alerts"""
        alerts = []
        
        if response_time > 2.0:
            alerts.append({
                'type': 'warning',
                'message': f'Slow response time: {response_time:.2f}s',
                'timestamp': datetime.utcnow()
            })
        
        if query_count > 50:
            alerts.append({
                'type': 'warning',
                'message': f'High query count: {query_count} queries',
                'timestamp': datetime.utcnow()
            })
        
        if cache_hit_rate < 50:
            alerts.append({
                'type': 'info',
                'message': f'Low cache hit rate: {cache_hit_rate:.1f}%',
                'timestamp': datetime.utcnow()
            })
        
        for alert in alerts:
            self.alerts.append(alert)
    
    def _check_system_alerts(self, memory_percent: float, cpu_percent: float, active_connections: int):
        """Check for system-level alerts"""
        alerts = []
        
        if memory_percent > 85:
            alerts.append({
                'type': 'critical',
                'message': f'High memory usage: {memory_percent:.1f}%',
                'timestamp': datetime.utcnow()
            })
        
        if cpu_percent > 80:
            alerts.append({
                'type': 'warning',
                'message': f'High CPU usage: {cpu_percent:.1f}%',
                'timestamp': datetime.utcnow()
            })
        
        if active_connections > 15:  # Assuming pool size of 20
            alerts.append({
                'type': 'warning',
                'message': f'High database connections: {active_connections}',
                'timestamp': datetime.utcnow()
            })
        
        for alert in alerts:
            self.alerts.append(alert)
    
    def get_metrics_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get performance metrics summary for the last N minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        with self.lock:
            summary = {}
            
            for metric_name, metric_data in self.metrics.items():
                recent_data = [
                    item['value'] for item in metric_data 
                    if item['timestamp'] >= cutoff_time
                ]
                
                if recent_data:
                    summary[metric_name] = {
                        'current': recent_data[-1] if recent_data else 0,
                        'average': sum(recent_data) / len(recent_data),
                        'min': min(recent_data),
                        'max': max(recent_data),
                        'count': len(recent_data)
                    }
                else:
                    summary[metric_name] = {
                        'current': 0, 'average': 0, 'min': 0, 'max': 0, 'count': 0
                    }
            
            # Recent slow queries
            recent_slow_queries = [
                query for query in self.slow_queries 
                if query['timestamp'] >= cutoff_time
            ]
            
            # Recent errors
            recent_errors = [
                error for error in self.error_log 
                if error['timestamp'] >= cutoff_time
            ]
            
            # Recent alerts
            recent_alerts = [
                alert for alert in self.alerts 
                if alert['timestamp'] >= cutoff_time
            ]
            
            summary['slow_queries'] = recent_slow_queries
            summary['errors'] = recent_errors
            summary['alerts'] = recent_alerts
            
            return summary
    
    def get_time_series_data(self, metric_name: str, minutes: int = 60) -> List[Dict]:
        """Get time series data for a specific metric"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        with self.lock:
            if metric_name in self.metrics:
                return [
                    {
                        'timestamp': item['timestamp'].isoformat(),
                        'value': item['value']
                    }
                    for item in self.metrics[metric_name]
                    if item['timestamp'] >= cutoff_time
                ]
            return []

# Global performance collector
performance_collector = PerformanceCollector()

class PerformanceAnalyzer:
    """Analyzes performance data and provides recommendations"""
    
    @staticmethod
    def analyze_performance(summary: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance data and generate recommendations"""
        recommendations = []
        health_score = 100
        
        # Analyze response times
        avg_response_time = summary.get('response_times', {}).get('average', 0)
        if avg_response_time > 1.0:
            recommendations.append({
                'type': 'warning',
                'category': 'Response Time',
                'message': f'Average response time is {avg_response_time:.2f}s. Consider optimizing slow endpoints.',
                'priority': 'high' if avg_response_time > 2.0 else 'medium'
            })
            health_score -= 15 if avg_response_time > 2.0 else 10
        
        # Analyze query counts
        avg_queries = summary.get('query_counts', {}).get('average', 0)
        if avg_queries > 20:
            recommendations.append({
                'type': 'warning',
                'category': 'Database Queries',
                'message': f'Average {avg_queries:.1f} queries per request. Look for N+1 query problems.',
                'priority': 'high' if avg_queries > 50 else 'medium'
            })
            health_score -= 20 if avg_queries > 50 else 10
        
        # Analyze cache hit rate
        avg_cache_hit_rate = summary.get('cache_hit_rates', {}).get('average', 0)
        if avg_cache_hit_rate < 70:
            recommendations.append({
                'type': 'info',
                'category': 'Caching',
                'message': f'Cache hit rate is {avg_cache_hit_rate:.1f}%. Consider caching more data.',
                'priority': 'medium' if avg_cache_hit_rate < 50 else 'low'
            })
            health_score -= 15 if avg_cache_hit_rate < 50 else 5
        
        # Analyze memory usage
        avg_memory = summary.get('memory_usage', {}).get('average', 0)
        if avg_memory > 80:
            recommendations.append({
                'type': 'critical',
                'category': 'Memory Usage',
                'message': f'Memory usage is {avg_memory:.1f}%. Consider scaling or optimizing memory usage.',
                'priority': 'critical' if avg_memory > 90 else 'high'
            })
            health_score -= 25 if avg_memory > 90 else 15
        
        # Analyze CPU usage
        avg_cpu = summary.get('cpu_usage', {}).get('average', 0)
        if avg_cpu > 70:
            recommendations.append({
                'type': 'warning',
                'category': 'CPU Usage',
                'message': f'CPU usage is {avg_cpu:.1f}%. Consider optimizing CPU-intensive operations.',
                'priority': 'high' if avg_cpu > 85 else 'medium'
            })
            health_score -= 20 if avg_cpu > 85 else 10
        
        # Analyze slow queries
        slow_query_count = len(summary.get('slow_queries', []))
        if slow_query_count > 10:
            recommendations.append({
                'type': 'warning',
                'category': 'Database Performance',
                'message': f'{slow_query_count} slow queries detected. Review and optimize database queries.',
                'priority': 'high'
            })
            health_score -= 15
        
        # Analyze errors
        error_count = len(summary.get('errors', []))
        if error_count > 5:
            recommendations.append({
                'type': 'critical',
                'category': 'Error Rate',
                'message': f'{error_count} errors detected. Investigate and fix application errors.',
                'priority': 'critical'
            })
            health_score -= 30
        
        return {
            'health_score': max(0, health_score),
            'recommendations': recommendations,
            'status': PerformanceAnalyzer._get_health_status(health_score)
        }
    
    @staticmethod
    def _get_health_status(health_score: int) -> str:
        """Get health status based on score"""
        if health_score >= 90:
            return 'excellent'
        elif health_score >= 75:
            return 'good'
        elif health_score >= 60:
            return 'fair'
        elif health_score >= 40:
            return 'poor'
        else:
            return 'critical'

# Routes for performance monitoring dashboard
@performance_bp.route('/')
@login_required
@require_role('admin')
def dashboard():
    """Performance monitoring dashboard"""
    return render_template('admin_management/performance_dashboard.html')

@performance_bp.route('/api/metrics')
@login_required
@require_role('admin')
def get_metrics():
    """API endpoint to get performance metrics"""
    minutes = request.args.get('minutes', 60, type=int)
    summary = performance_collector.get_metrics_summary(minutes)
    analysis = PerformanceAnalyzer.analyze_performance(summary)
    
    return jsonify({
        'success': True,
        'data': {
            'summary': summary,
            'analysis': analysis,
            'cache_stats': cache.get_stats(),
            'db_stats': ConnectionPoolOptimizer.monitor_connection_usage()
        }
    })

@performance_bp.route('/api/timeseries/<metric_name>')
@login_required
@require_role('admin')
def get_timeseries(metric_name):
    """API endpoint to get time series data for a metric"""
    minutes = request.args.get('minutes', 60, type=int)
    data = performance_collector.get_time_series_data(metric_name, minutes)
    
    return jsonify({
        'success': True,
        'data': data
    })

@performance_bp.route('/api/cache/clear', methods=['POST'])
@login_required
@require_role('admin')
def clear_cache():
    """API endpoint to clear cache"""
    try:
        cache.clear()
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@performance_bp.route('/api/cache/health')
@login_required
@require_role('admin')
def cache_health():
    """API endpoint to get cache health status"""
    health = CacheMaintenance.get_cache_health()
    return jsonify({
        'success': True,
        'data': health
    })

@performance_bp.route('/api/optimize/indexes', methods=['POST'])
@login_required
@require_role('admin')
def optimize_indexes():
    """API endpoint to create performance indexes"""
    try:
        from modules.core.database_optimization import IndexOptimizer
        IndexOptimizer.create_performance_indexes()
        
        return jsonify({
            'success': True,
            'message': 'Database indexes optimized successfully'
        })
    except Exception as e:
        logger.error(f"Index optimization failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def setup_performance_monitoring(app):
    """Setup performance monitoring for the application"""
    app.register_blueprint(performance_bp)
    
    # Hook into request lifecycle
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.start_query_count = perf_monitor.query_count
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time
            query_count = perf_monitor.query_count - g.start_query_count
            cache_stats = cache.get_stats()
            cache_hit_rate = cache_stats.get('overall_hit_rate', 0)
            
            # Record metrics
            performance_collector.add_request_metric(
                response_time=response_time,
                query_count=query_count,
                cache_hit_rate=cache_hit_rate,
                error=(response.status_code >= 400)
            )
            
            # Record slow queries
            for slow_query in perf_monitor.slow_queries:
                performance_collector.add_slow_query(
                    query=slow_query['statement'],
                    duration=slow_query['duration']
                )
        
        return response
    
    logger.info("Performance monitoring setup completed")

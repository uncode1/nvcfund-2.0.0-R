"""
Performance Optimization Module for NVC Banking Platform
Provides caching, query optimization, and performance monitoring utilities
"""

import time
import functools
from typing import Any, Callable, Dict, List, Optional
from flask import current_app, request, g
from flask_caching import Cache
from sqlalchemy import event
from sqlalchemy.engine import Engine
from modules.core.extensions import db
import logging

# Initialize cache
cache = Cache()

class PerformanceMonitor:
    """Monitor and track application performance metrics"""
    
    def __init__(self):
        self.query_count = 0
        self.query_time = 0.0
        self.slow_queries = []
        self.cache_hits = 0
        self.cache_misses = 0
    
    def reset(self):
        """Reset performance counters"""
        self.query_count = 0
        self.query_time = 0.0
        self.slow_queries = []
        self.cache_hits = 0
        self.cache_misses = 0
    
    def add_query(self, duration: float, statement: str):
        """Add query performance data"""
        self.query_count += 1
        self.query_time += duration
        
        # Track slow queries (>100ms)
        if duration > 0.1:
            self.slow_queries.append({
                'duration': duration,
                'statement': statement[:200] + '...' if len(statement) > 200 else statement
            })
    
    def cache_hit(self):
        """Record cache hit"""
        self.cache_hits += 1
    
    def cache_miss(self):
        """Record cache miss"""
        self.cache_misses += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        cache_total = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / cache_total * 100) if cache_total > 0 else 0
        
        return {
            'query_count': self.query_count,
            'total_query_time': round(self.query_time, 3),
            'average_query_time': round(self.query_time / self.query_count, 3) if self.query_count > 0 else 0,
            'slow_queries': len(self.slow_queries),
            'cache_hit_rate': round(cache_hit_rate, 2),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses
        }

# Global performance monitor
perf_monitor = PerformanceMonitor()

def setup_performance_monitoring(app):
    """Setup performance monitoring for the application"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        perf_monitor.reset()
    
    @app.after_request
    def after_request(response):
        total_time = time.time() - g.start_time
        stats = perf_monitor.get_stats()
        
        # Add performance headers
        response.headers['X-Response-Time'] = f"{total_time:.3f}s"
        response.headers['X-Query-Count'] = str(stats['query_count'])
        response.headers['X-Cache-Hit-Rate'] = f"{stats['cache_hit_rate']}%"
        
        # Log performance metrics
        if current_app.config.get('LOG_PERFORMANCE', False):
            current_app.logger.info(
                f"Performance: {request.method} {request.path} "
                f"Time: {total_time:.3f}s "
                f"Queries: {stats['query_count']} "
                f"Cache: {stats['cache_hit_rate']}%"
            )
        
        # Log slow requests
        if total_time > 1.0:  # Requests taking more than 1 second
            current_app.logger.warning(
                f"Slow request: {request.method} {request.path} "
                f"Time: {total_time:.3f}s "
                f"Stats: {stats}"
            )
        
        return response

# Database query monitoring
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    perf_monitor.add_query(total, statement)

class CacheManager:
    """Advanced caching utilities"""
    
    @staticmethod
    def cache_key(*args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        return ":".join(key_parts)
    
    @staticmethod
    def invalidate_pattern(pattern: str):
        """Invalidate cache keys matching pattern"""
        # This would require Redis SCAN command for pattern matching
        # For now, we'll implement basic invalidation
        if hasattr(cache.cache, 'delete_many'):
            # Get all keys matching pattern (Redis implementation)
            keys = cache.cache._read_clients.keys(pattern)
            if keys:
                cache.delete_many(*keys)
    
    @staticmethod
    def warm_cache(func: Callable, *args, **kwargs):
        """Pre-warm cache with function result"""
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            current_app.logger.error(f"Cache warming failed: {e}")
            return None

def cached_query(timeout: int = 300, key_prefix: str = None):
    """Decorator for caching database query results"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = f"{prefix}:{CacheManager.cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                perf_monitor.cache_hit()
                return result
            
            # Cache miss - execute function
            perf_monitor.cache_miss()
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, timeout=timeout)
            return result
        
        # Add cache invalidation method
        wrapper.invalidate = lambda *args, **kwargs: cache.delete(
            f"{key_prefix or func.__module__}.{func.__name__}:{CacheManager.cache_key(*args, **kwargs)}"
        )
        
        return wrapper
    return decorator

class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def eager_load_relationships(query, *relationships):
        """Add eager loading for relationships to prevent N+1 queries"""
        from sqlalchemy.orm import joinedload, selectinload
        
        for relationship in relationships:
            if isinstance(relationship, str):
                # Simple relationship name
                query = query.options(joinedload(relationship))
            elif isinstance(relationship, tuple):
                # Nested relationship
                query = query.options(joinedload(*relationship))
            else:
                # Custom loader option
                query = query.options(relationship)
        
        return query
    
    @staticmethod
    def paginate_efficiently(query, page: int, per_page: int, max_per_page: int = 100):
        """Efficient pagination with limits"""
        per_page = min(per_page, max_per_page)
        
        # Use window functions for better performance on large datasets
        if page > 100:  # For very large page numbers, use cursor-based pagination
            current_app.logger.warning(f"Large page number requested: {page}")
        
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
            max_per_page=max_per_page
        )
    
    @staticmethod
    def bulk_insert(model_class, data_list: List[Dict], batch_size: int = 1000):
        """Efficient bulk insert operation"""
        try:
            # Process in batches
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                db.session.bulk_insert_mappings(model_class, batch)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Bulk insert failed: {e}")
            return False
    
    @staticmethod
    def bulk_update(model_class, data_list: List[Dict], batch_size: int = 1000):
        """Efficient bulk update operation"""
        try:
            # Process in batches
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                db.session.bulk_update_mappings(model_class, batch)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Bulk update failed: {e}")
            return False

class AssetOptimizer:
    """Static asset optimization utilities"""
    
    @staticmethod
    def minify_css(css_content: str) -> str:
        """Basic CSS minification"""
        import re
        
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove extra whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        
        # Remove whitespace around specific characters
        css_content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_content)
        
        return css_content.strip()
    
    @staticmethod
    def minify_js(js_content: str) -> str:
        """Basic JavaScript minification"""
        import re
        
        # Remove single-line comments (but preserve URLs)
        js_content = re.sub(r'(?<!:)//.*$', '', js_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove extra whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        
        # Remove whitespace around operators
        js_content = re.sub(r'\s*([{}();,=+\-*/<>!&|])\s*', r'\1', js_content)
        
        return js_content.strip()
    
    @staticmethod
    def generate_asset_hash(content: str) -> str:
        """Generate hash for asset versioning"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()[:8]

def performance_test(func):
    """Decorator to measure function performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        current_app.logger.info(
            f"Performance test: {func.__name__} took {duration:.3f}s"
        )
        
        return result
    return wrapper

class MemoryOptimizer:
    """Memory usage optimization utilities"""
    
    @staticmethod
    def clear_session():
        """Clear SQLAlchemy session to free memory"""
        db.session.expunge_all()
    
    @staticmethod
    def optimize_query_result(result):
        """Optimize query result for memory usage"""
        if hasattr(result, '_sa_instance_state'):
            # Detach from session to reduce memory overhead
            db.session.expunge(result)
        return result
    
    @staticmethod
    def batch_process(items: List, batch_size: int = 100, processor: Callable = None):
        """Process items in batches to manage memory"""
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            if processor:
                processor(batch)
            
            # Clear session after each batch
            MemoryOptimizer.clear_session()
            
            yield batch

# Performance configuration
class PerformanceConfig:
    """Performance-related configuration"""
    
    # Cache settings
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'nvc_banking:'
    
    # Query optimization
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30,
        'echo': False  # Set to True for query debugging
    }
    
    # Performance monitoring
    LOG_PERFORMANCE = True
    SLOW_QUERY_THRESHOLD = 0.1  # 100ms
    
    # Asset optimization
    MINIFY_ASSETS = True
    ASSET_VERSIONING = True
    
    # Memory optimization
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    @classmethod
    def init_app(cls, app):
        """Initialize performance configuration"""
        # Set up caching
        cache.init_app(app)
        
        # Set up performance monitoring
        setup_performance_monitoring(app)
        
        # Configure SQLAlchemy for performance
        app.config.update(cls.SQLALCHEMY_ENGINE_OPTIONS)

# Utility functions for common performance patterns
def get_or_create_cached(model_class, cache_key: str, create_func: Callable, timeout: int = 300):
    """Get object from cache or create and cache it"""
    obj = cache.get(cache_key)
    if obj is None:
        obj = create_func()
        cache.set(cache_key, obj, timeout=timeout)
        perf_monitor.cache_miss()
    else:
        perf_monitor.cache_hit()
    
    return obj

def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a specific user"""
    patterns = [
        f"user:{user_id}:*",
        f"accounts:{user_id}:*",
        f"transactions:{user_id}:*",
        f"dashboard:{user_id}:*"
    ]
    
    for pattern in patterns:
        CacheManager.invalidate_pattern(pattern)

def warm_user_cache(user_id: int):
    """Pre-warm cache for user data"""
    from modules.auth.services import AuthService
    from modules.banking.services import BankingService
    
    auth_service = AuthService()
    banking_service = BankingService()
    
    # Warm common user data
    CacheManager.warm_cache(auth_service.get_user_profile, user_id)
    CacheManager.warm_cache(banking_service.get_user_accounts, user_id)
    CacheManager.warm_cache(banking_service.get_recent_transactions, user_id, limit=10)

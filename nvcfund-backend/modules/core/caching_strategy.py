"""
Advanced Caching Strategy for NVC Banking Platform
Implements multi-level caching with Redis, application cache, and database query cache
"""

import json
import pickle
import time
import functools
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from flask import current_app, request, g
from flask_caching import Cache
import redis
import logging

logger = logging.getLogger(__name__)

class CacheConfig:
    """Cache configuration settings"""
    
    # Cache types
    REDIS_CACHE = 'redis'
    MEMORY_CACHE = 'simple'
    
    # Cache timeouts (in seconds)
    SHORT_CACHE = 60          # 1 minute
    MEDIUM_CACHE = 300        # 5 minutes
    LONG_CACHE = 1800         # 30 minutes
    EXTENDED_CACHE = 3600     # 1 hour
    DAILY_CACHE = 86400       # 24 hours
    
    # Cache key prefixes
    USER_PREFIX = 'user'
    ACCOUNT_PREFIX = 'account'
    TRANSACTION_PREFIX = 'transaction'
    DASHBOARD_PREFIX = 'dashboard'
    API_PREFIX = 'api'
    SESSION_PREFIX = 'session'
    
    # Cache invalidation patterns
    INVALIDATION_PATTERNS = {
        'user_data': ['user:{user_id}:*', 'dashboard:{user_id}:*'],
        'account_data': ['account:{account_id}:*', 'user:{user_id}:accounts:*'],
        'transaction_data': ['transaction:{account_id}:*', 'account:{account_id}:*'],
        'system_data': ['system:*', 'config:*']
    }

class MultiLevelCache:
    """Multi-level caching system with L1 (memory) and L2 (Redis) cache"""
    
    def __init__(self, app=None):
        self.app = app
        self.l1_cache = Cache()  # Memory cache (L1)
        self.l2_cache = None     # Redis cache (L2)
        self.stats = {
            'l1_hits': 0,
            'l1_misses': 0,
            'l2_hits': 0,
            'l2_misses': 0,
            'sets': 0,
            'deletes': 0
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize caching with Flask app"""
        self.app = app
        
        # Configure L1 cache (memory)
        app.config.setdefault('CACHE_TYPE', 'simple')
        app.config.setdefault('CACHE_DEFAULT_TIMEOUT', CacheConfig.MEDIUM_CACHE)
        self.l1_cache.init_app(app)
        
        # Configure L2 cache (Redis)
        redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self.l2_cache = redis.from_url(redis_url, decode_responses=True)
            self.l2_cache.ping()  # Test connection
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis cache initialization failed: {e}")
            self.l2_cache = None
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for Redis storage"""
        try:
            return json.dumps(value, default=str)
        except (TypeError, ValueError):
            # Fallback to pickle for complex objects
            return pickle.dumps(value).hex()
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from Redis storage"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # Try pickle deserialization
            try:
                return pickle.loads(bytes.fromhex(value))
            except Exception:
                return value
    
    def get(self, key: str) -> Any:
        """Get value from cache (L1 first, then L2)"""
        # Try L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            self.stats['l1_hits'] += 1
            return value
        
        self.stats['l1_misses'] += 1
        
        # Try L2 cache (Redis)
        if self.l2_cache:
            try:
                redis_value = self.l2_cache.get(key)
                if redis_value is not None:
                    self.stats['l2_hits'] += 1
                    deserialized_value = self._deserialize_value(redis_value)
                    
                    # Store in L1 cache for faster access
                    self.l1_cache.set(key, deserialized_value, timeout=CacheConfig.SHORT_CACHE)
                    
                    return deserialized_value
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        self.stats['l2_misses'] += 1
        return None
    
    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """Set value in both cache levels"""
        timeout = timeout or CacheConfig.MEDIUM_CACHE
        
        try:
            # Set in L1 cache
            self.l1_cache.set(key, value, timeout=min(timeout, CacheConfig.SHORT_CACHE))
            
            # Set in L2 cache (Redis)
            if self.l2_cache:
                serialized_value = self._serialize_value(value)
                self.l2_cache.setex(key, timeout, serialized_value)
            
            self.stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from both cache levels"""
        try:
            # Delete from L1 cache
            self.l1_cache.delete(key)
            
            # Delete from L2 cache
            if self.l2_cache:
                self.l2_cache.delete(key)
            
            self.stats['deletes'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern (Redis only)"""
        if not self.l2_cache:
            return 0
        
        try:
            keys = self.l2_cache.keys(pattern)
            if keys:
                deleted = self.l2_cache.delete(*keys)
                # Also try to delete from L1 cache
                for key in keys:
                    self.l1_cache.delete(key)
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache pattern delete error: {e}")
            return 0
    
    def clear(self) -> bool:
        """Clear both cache levels"""
        try:
            self.l1_cache.clear()
            if self.l2_cache:
                self.l2_cache.flushdb()
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = (self.stats['l1_hits'] + self.stats['l1_misses'] + 
                         self.stats['l2_hits'] + self.stats['l2_misses'])
        
        if total_requests > 0:
            l1_hit_rate = (self.stats['l1_hits'] / total_requests) * 100
            l2_hit_rate = (self.stats['l2_hits'] / total_requests) * 100
            overall_hit_rate = ((self.stats['l1_hits'] + self.stats['l2_hits']) / total_requests) * 100
        else:
            l1_hit_rate = l2_hit_rate = overall_hit_rate = 0
        
        return {
            **self.stats,
            'l1_hit_rate': round(l1_hit_rate, 2),
            'l2_hit_rate': round(l2_hit_rate, 2),
            'overall_hit_rate': round(overall_hit_rate, 2),
            'total_requests': total_requests
        }

# Global cache instance
cache = MultiLevelCache()

class CacheManager:
    """High-level cache management utilities"""
    
    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        return ":".join(key_parts)
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """Invalidate all cache entries for a user"""
        patterns = CacheConfig.INVALIDATION_PATTERNS['user_data']
        for pattern in patterns:
            cache.delete_pattern(pattern.format(user_id=user_id))
    
    @staticmethod
    def invalidate_account_cache(account_id: int, user_id: int = None):
        """Invalidate cache entries for an account"""
        patterns = CacheConfig.INVALIDATION_PATTERNS['account_data']
        for pattern in patterns:
            if '{user_id}' in pattern and user_id:
                cache.delete_pattern(pattern.format(account_id=account_id, user_id=user_id))
            else:
                cache.delete_pattern(pattern.format(account_id=account_id))
    
    @staticmethod
    def warm_user_cache(user_id: int):
        """Pre-warm cache with user data"""
        from modules.auth.services import AuthService
        from modules.banking.services import BankingService
        
        try:
            auth_service = AuthService()
            banking_service = BankingService()
            
            # Warm user profile
            user_key = CacheManager.generate_key(CacheConfig.USER_PREFIX, user_id, 'profile')
            user_data = auth_service.get_user_profile(user_id)
            cache.set(user_key, user_data, CacheConfig.LONG_CACHE)
            
            # Warm account data
            accounts_key = CacheManager.generate_key(CacheConfig.USER_PREFIX, user_id, 'accounts')
            accounts_data = banking_service.get_user_accounts(user_id)
            cache.set(accounts_key, accounts_data, CacheConfig.MEDIUM_CACHE)
            
            logger.info(f"Cache warmed for user {user_id}")
            
        except Exception as e:
            logger.error(f"Cache warming failed for user {user_id}: {e}")

def cached(timeout: int = None, key_prefix: str = None, unless: Callable = None):
    """Advanced caching decorator with invalidation support"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check unless condition
            if unless and unless():
                return func(*args, **kwargs)
            
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = f"{prefix}:{CacheManager.generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout or CacheConfig.MEDIUM_CACHE)
            
            return result
        
        # Add cache invalidation method
        wrapper.invalidate = lambda *args, **kwargs: cache.delete(
            f"{key_prefix or func.__module__}.{func.__name__}:{CacheManager.generate_key(*args, **kwargs)}"
        )
        
        return wrapper
    return decorator

def cache_response(timeout: int = None, key_func: Callable = None):
    """Cache HTTP responses"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"response:{request.endpoint}:{request.view_args}:{request.args}"
            
            # Try to get cached response
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # Execute function and cache response
            response = func(*args, **kwargs)
            cache.set(cache_key, response, timeout or CacheConfig.SHORT_CACHE)
            
            return response
        
        return wrapper
    return decorator

class SessionCache:
    """Session-based caching for user-specific data"""
    
    @staticmethod
    def get(key: str, user_id: int = None) -> Any:
        """Get value from session cache"""
        if user_id is None:
            from flask_login import current_user
            user_id = current_user.id if current_user.is_authenticated else None
        
        if user_id:
            session_key = f"{CacheConfig.SESSION_PREFIX}:{user_id}:{key}"
            return cache.get(session_key)
        return None
    
    @staticmethod
    def set(key: str, value: Any, timeout: int = None, user_id: int = None) -> bool:
        """Set value in session cache"""
        if user_id is None:
            from flask_login import current_user
            user_id = current_user.id if current_user.is_authenticated else None
        
        if user_id:
            session_key = f"{CacheConfig.SESSION_PREFIX}:{user_id}:{key}"
            return cache.set(session_key, value, timeout or CacheConfig.MEDIUM_CACHE)
        return False
    
    @staticmethod
    def delete(key: str, user_id: int = None) -> bool:
        """Delete value from session cache"""
        if user_id is None:
            from flask_login import current_user
            user_id = current_user.id if current_user.is_authenticated else None
        
        if user_id:
            session_key = f"{CacheConfig.SESSION_PREFIX}:{user_id}:{key}"
            return cache.delete(session_key)
        return False
    
    @staticmethod
    def clear_user_session(user_id: int) -> int:
        """Clear all session cache for a user"""
        pattern = f"{CacheConfig.SESSION_PREFIX}:{user_id}:*"
        return cache.delete_pattern(pattern)

class QueryCache:
    """Database query result caching"""
    
    @staticmethod
    def cache_query_result(query_hash: str, result: Any, timeout: int = None):
        """Cache database query result"""
        cache_key = f"query:{query_hash}"
        cache.set(cache_key, result, timeout or CacheConfig.MEDIUM_CACHE)
    
    @staticmethod
    def get_cached_query_result(query_hash: str) -> Any:
        """Get cached database query result"""
        cache_key = f"query:{query_hash}"
        return cache.get(cache_key)
    
    @staticmethod
    def invalidate_table_cache(table_name: str):
        """Invalidate all cached queries for a table"""
        pattern = f"query:*{table_name}*"
        cache.delete_pattern(pattern)

def setup_caching(app):
    """Setup caching for Flask application"""
    cache.init_app(app)
    
    # Add cache statistics to app context
    @app.context_processor
    def inject_cache_stats():
        if app.debug:
            return {'cache_stats': cache.get_stats()}
        return {}
    
    # Cache warming on startup
    if not app.debug:
        @app.before_first_request
        def warm_cache():
            # Warm system-wide cache
            try:
                # Cache system configuration
                system_key = f"{CacheConfig.API_PREFIX}:system:config"
                system_config = {'version': '2.0.0', 'maintenance': False}
                cache.set(system_key, system_config, CacheConfig.DAILY_CACHE)
                
                logger.info("System cache warmed")
            except Exception as e:
                logger.error(f"Cache warming failed: {e}")
    
    logger.info("Caching system initialized")

# Cache monitoring and maintenance
class CacheMaintenance:
    """Cache maintenance utilities"""
    
    @staticmethod
    def cleanup_expired_keys():
        """Clean up expired cache keys (Redis handles this automatically)"""
        if cache.l2_cache:
            try:
                # Get memory usage info
                info = cache.l2_cache.info('memory')
                used_memory = info.get('used_memory_human', 'Unknown')
                logger.info(f"Redis memory usage: {used_memory}")
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    @staticmethod
    def get_cache_health() -> Dict[str, Any]:
        """Get cache health status"""
        health = {
            'l1_cache': True,
            'l2_cache': False,
            'stats': cache.get_stats()
        }
        
        # Test Redis connection
        if cache.l2_cache:
            try:
                cache.l2_cache.ping()
                health['l2_cache'] = True
            except Exception:
                health['l2_cache'] = False
        
        return health

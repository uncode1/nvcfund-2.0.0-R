"""
Database Optimization Module for NVC Banking Platform
Fixes N+1 queries and provides optimized database access patterns
"""

from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import joinedload, selectinload, subqueryload, contains_eager
from sqlalchemy import and_, or_, func, text
from modules.core.extensions import db
from modules.core.performance import cached_query, QueryOptimizer
import logging

logger = logging.getLogger(__name__)

class OptimizedQueries:
    """Optimized database queries to prevent N+1 problems"""
    
    @staticmethod
    @cached_query(timeout=300, key_prefix="user_with_accounts")
    def get_user_with_accounts(user_id: int):
        """Get user with all accounts in a single query"""
        from modules.auth.models import User
        from modules.banking.models import BankAccount
        
        return User.query.options(
            joinedload(User.bank_accounts).joinedload(BankAccount.cards),
            joinedload(User.bank_accounts).joinedload(BankAccount.recent_transactions)
        ).filter(User.id == user_id).first()
    
    @staticmethod
    @cached_query(timeout=180, key_prefix="account_with_transactions")
    def get_account_with_transactions(account_id: int, limit: int = 50):
        """Get account with recent transactions in optimized way"""
        from modules.banking.models import BankAccount, Transaction
        
        # Use subquery to limit transactions per account
        subq = db.session.query(Transaction.id).filter(
            Transaction.account_id == account_id
        ).order_by(Transaction.created_at.desc()).limit(limit).subquery()
        
        return BankAccount.query.options(
            selectinload(BankAccount.transactions).filter(
                Transaction.id.in_(subq)
            ).options(
                joinedload(Transaction.category),
                joinedload(Transaction.merchant)
            )
        ).filter(BankAccount.id == account_id).first()
    
    @staticmethod
    @cached_query(timeout=600, key_prefix="user_dashboard_data")
    def get_user_dashboard_data(user_id: int):
        """Get all dashboard data in optimized queries"""
        from modules.auth.models import User
        from modules.banking.models import BankAccount, Transaction, Card
        
        # Get user with basic account info
        user = User.query.options(
            joinedload(User.bank_accounts).options(
                joinedload(BankAccount.account_type_info),
                selectinload(BankAccount.cards).options(
                    joinedload(Card.card_type_info)
                )
            )
        ).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        # Get recent transactions across all accounts
        account_ids = [acc.id for acc in user.bank_accounts]
        recent_transactions = Transaction.query.options(
            joinedload(Transaction.account).options(
                joinedload(BankAccount.account_type_info)
            ),
            joinedload(Transaction.category),
            joinedload(Transaction.merchant)
        ).filter(
            Transaction.account_id.in_(account_ids)
        ).order_by(Transaction.created_at.desc()).limit(10).all()
        
        return {
            'user': user,
            'recent_transactions': recent_transactions,
            'total_balance': sum(acc.current_balance for acc in user.bank_accounts),
            'account_count': len(user.bank_accounts),
            'card_count': sum(len(acc.cards) for acc in user.bank_accounts)
        }
    
    @staticmethod
    @cached_query(timeout=300, key_prefix="account_summary")
    def get_account_summary(user_id: int):
        """Get account summary with aggregated data"""
        from modules.banking.models import BankAccount, Transaction
        
        # Use database aggregation instead of Python loops
        summary = db.session.query(
            BankAccount.account_type,
            func.count(BankAccount.id).label('account_count'),
            func.sum(BankAccount.current_balance).label('total_balance'),
            func.sum(BankAccount.available_balance).label('available_balance')
        ).filter(
            BankAccount.account_holder_id == user_id,
            BankAccount.status == 'active'
        ).group_by(BankAccount.account_type).all()
        
        # Get transaction counts
        transaction_counts = db.session.query(
            BankAccount.account_type,
            func.count(Transaction.id).label('transaction_count')
        ).join(Transaction).filter(
            BankAccount.account_holder_id == user_id,
            Transaction.created_at >= func.date_trunc('month', func.current_date())
        ).group_by(BankAccount.account_type).all()
        
        return {
            'account_summary': summary,
            'transaction_counts': transaction_counts
        }
    
    @staticmethod
    @cached_query(timeout=120, key_prefix="transaction_history")
    def get_transaction_history(account_id: int, page: int = 1, per_page: int = 50):
        """Get paginated transaction history with optimizations"""
        from modules.banking.models import Transaction
        
        query = Transaction.query.options(
            joinedload(Transaction.account).options(
                joinedload('account_holder')
            ),
            joinedload(Transaction.category),
            joinedload(Transaction.merchant),
            joinedload(Transaction.related_transfer)
        ).filter(Transaction.account_id == account_id)
        
        return QueryOptimizer.paginate_efficiently(
            query.order_by(Transaction.created_at.desc()),
            page=page,
            per_page=per_page
        )
    
    @staticmethod
    @cached_query(timeout=300, key_prefix="user_cards")
    def get_user_cards_optimized(user_id: int):
        """Get all user cards with account info in single query"""
        from modules.banking.models import Card, BankAccount
        
        return Card.query.options(
            joinedload(Card.account).options(
                joinedload(BankAccount.account_holder),
                joinedload(BankAccount.account_type_info)
            ),
            joinedload(Card.card_type_info),
            selectinload(Card.recent_transactions).options(
                joinedload('merchant'),
                joinedload('category')
            )
        ).join(BankAccount).filter(
            BankAccount.account_holder_id == user_id,
            Card.status.in_(['active', 'blocked'])
        ).all()
    
    @staticmethod
    def get_monthly_spending_analysis(user_id: int, months: int = 6):
        """Get spending analysis using database aggregation"""
        from modules.banking.models import BankAccount, Transaction
        
        # Use raw SQL for complex aggregation
        query = text("""
            SELECT 
                DATE_TRUNC('month', t.created_at) as month,
                tc.name as category,
                SUM(t.amount) as total_amount,
                COUNT(t.id) as transaction_count,
                AVG(t.amount) as avg_amount
            FROM transactions t
            JOIN bank_accounts ba ON t.account_id = ba.id
            LEFT JOIN transaction_categories tc ON t.category_id = tc.id
            WHERE ba.account_holder_id = :user_id
                AND t.transaction_type = 'debit'
                AND t.created_at >= CURRENT_DATE - INTERVAL ':months months'
                AND t.status = 'completed'
            GROUP BY DATE_TRUNC('month', t.created_at), tc.name
            ORDER BY month DESC, total_amount DESC
        """)
        
        result = db.session.execute(query, {
            'user_id': user_id,
            'months': months
        })
        
        return result.fetchall()
    
    @staticmethod
    @cached_query(timeout=900, key_prefix="compliance_report")
    def get_compliance_report_data(start_date, end_date):
        """Get compliance report data with optimized queries"""
        from modules.banking.models import Transaction, BankAccount
        from modules.auth.models import User
        
        # Large transaction report
        large_transactions = db.session.query(
            Transaction.id,
            Transaction.amount,
            Transaction.description,
            Transaction.created_at,
            User.username,
            User.email,
            BankAccount.account_number
        ).join(BankAccount).join(User).filter(
            Transaction.amount >= 10000,  # Large transaction threshold
            Transaction.created_at.between(start_date, end_date),
            Transaction.status == 'completed'
        ).order_by(Transaction.amount.desc()).all()
        
        # Suspicious activity patterns
        suspicious_patterns = db.session.query(
            User.id,
            User.username,
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount'),
            func.max(Transaction.amount).label('max_amount')
        ).join(BankAccount).join(Transaction).filter(
            Transaction.created_at.between(start_date, end_date)
        ).group_by(User.id, User.username).having(
            or_(
                func.count(Transaction.id) > 100,  # High frequency
                func.sum(Transaction.amount) > 100000  # High volume
            )
        ).all()
        
        return {
            'large_transactions': large_transactions,
            'suspicious_patterns': suspicious_patterns
        }

class BulkOperations:
    """Optimized bulk database operations"""
    
    @staticmethod
    def bulk_update_balances(balance_updates: List[Dict]):
        """Bulk update account balances efficiently"""
        from modules.banking.models import BankAccount
        
        try:
            # Use bulk update for better performance
            db.session.bulk_update_mappings(BankAccount, balance_updates)
            db.session.commit()
            
            # Invalidate related caches
            for update in balance_updates:
                account_id = update.get('id')
                if account_id:
                    OptimizedQueries.get_account_with_transactions.invalidate(account_id)
            
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Bulk balance update failed: {e}")
            return False
    
    @staticmethod
    def bulk_create_transactions(transactions: List[Dict]):
        """Bulk create transactions with optimizations"""
        from modules.banking.models import Transaction
        
        try:
            # Process in batches for memory efficiency
            batch_size = 1000
            for i in range(0, len(transactions), batch_size):
                batch = transactions[i:i + batch_size]
                db.session.bulk_insert_mappings(Transaction, batch)
            
            db.session.commit()
            
            # Invalidate related caches
            account_ids = set(t.get('account_id') for t in transactions)
            for account_id in account_ids:
                if account_id:
                    OptimizedQueries.get_account_with_transactions.invalidate(account_id)
            
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Bulk transaction creation failed: {e}")
            return False
    
    @staticmethod
    def bulk_update_user_preferences(user_updates: List[Dict]):
        """Bulk update user preferences"""
        from modules.auth.models import User
        
        try:
            db.session.bulk_update_mappings(User, user_updates)
            db.session.commit()
            
            # Invalidate user caches
            for update in user_updates:
                user_id = update.get('id')
                if user_id:
                    OptimizedQueries.get_user_with_accounts.invalidate(user_id)
                    OptimizedQueries.get_user_dashboard_data.invalidate(user_id)
            
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Bulk user update failed: {e}")
            return False

class IndexOptimizer:
    """Database index optimization utilities"""
    
    @staticmethod
    def create_performance_indexes():
        """Create indexes for better query performance"""
        indexes = [
            # Transaction indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_account_created "
            "ON transactions(account_id, created_at DESC)",
            
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_date "
            "ON transactions(account_id, created_at) WHERE status = 'completed'",
            
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_amount "
            "ON transactions(amount) WHERE amount >= 10000",
            
            # Account indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_holder_status "
            "ON bank_accounts(account_holder_id, status)",
            
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_type_balance "
            "ON bank_accounts(account_type, current_balance)",
            
            # User indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_active "
            "ON users(email) WHERE is_active = true",
            
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role_verified "
            "ON users(role, is_verified)",
            
            # Card indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cards_account_status "
            "ON cards(account_id, status)",
            
            # Audit log indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_action "
            "ON audit_logs(user_id, action, created_at DESC)",
            
            # System logs indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_system_logs_category_created "
            "ON system_logs(category, created_at DESC)",

            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_system_logs_user_level "
            "ON system_logs(user_id, log_level, created_at DESC)",

            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_system_logs_event_type "
            "ON system_logs(event_type, created_at DESC)",

            # Security logs indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_logs_severity_created "
            "ON security_logs(severity, created_at DESC)",

            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_logs_user_event "
            "ON security_logs(user_id, event_type, created_at DESC)",

            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_logs_ip_created "
            "ON security_logs(ip_address, created_at DESC)",

            # Transaction logs indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transaction_logs_transaction_event "
            "ON transaction_logs(transaction_id, event_type, created_at DESC)",

            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transaction_logs_account_created "
            "ON transaction_logs(from_account_id, created_at DESC)",

            # Compliance logs indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_compliance_logs_type_created "
            "ON compliance_logs(compliance_type, created_at DESC)",

            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_compliance_logs_user_risk "
            "ON compliance_logs(user_id, risk_level, created_at DESC)",

            # API logs indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_logs_endpoint_created "
            "ON api_logs(endpoint, created_at DESC)",

            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_logs_user_status "
            "ON api_logs(user_id, status_code, created_at DESC)",
        ]
        
        for index_sql in indexes:
            try:
                db.session.execute(text(index_sql))
                db.session.commit()
                logger.info(f"Created index: {index_sql}")
            except Exception as e:
                db.session.rollback()
                logger.warning(f"Index creation failed: {e}")
    
    @staticmethod
    def analyze_query_performance():
        """Analyze query performance and suggest optimizations"""
        # This would analyze slow query logs and suggest indexes
        # For now, we'll return basic recommendations
        
        recommendations = [
            "Consider adding composite indexes on frequently queried columns",
            "Use EXPLAIN ANALYZE to identify slow queries",
            "Consider partitioning large tables by date",
            "Regularly update table statistics with ANALYZE",
            "Monitor index usage with pg_stat_user_indexes"
        ]
        
        return recommendations

class ConnectionPoolOptimizer:
    """Database connection pool optimization"""
    
    @staticmethod
    def get_optimal_pool_settings(max_connections: int = 100):
        """Get optimal connection pool settings"""
        import multiprocessing
        
        # Calculate based on server resources
        cpu_count = multiprocessing.cpu_count()
        
        return {
            'pool_size': min(20, max_connections // 4),
            'max_overflow': min(30, max_connections // 3),
            'pool_recycle': 3600,  # 1 hour
            'pool_pre_ping': True,
            'pool_timeout': 30,
            'echo': False  # Set to True for debugging
        }
    
    @staticmethod
    def monitor_connection_usage():
        """Monitor database connection usage"""
        engine = db.engine
        pool = engine.pool
        
        return {
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalid': pool.invalid()
        }

# Query optimization decorators
def optimize_query(relationships: List[str] = None, cache_timeout: int = 300):
    """Decorator to optimize queries with eager loading and caching"""
    def decorator(func):
        @cached_query(timeout=cache_timeout)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Apply eager loading if result is a query
            if hasattr(result, 'options') and relationships:
                for rel in relationships:
                    result = result.options(joinedload(rel))
            
            return result
        return wrapper
    return decorator

def batch_process(batch_size: int = 100):
    """Decorator for batch processing large datasets"""
    def decorator(func):
        def wrapper(items, *args, **kwargs):
            results = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                batch_result = func(batch, *args, **kwargs)
                results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
                
                # Clear session after each batch to manage memory
                db.session.expunge_all()
            
            return results
        return wrapper
    return decorator

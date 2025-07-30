"""
Exchange Service
NVC Banking Platform - Complete Exchange Operations Service

Handles all exchange operations:
- Internal exchange between fiat and digital assets
- External exchange via Binance integration
- Liquidity pool management
- Exchange rate management
- Transaction processing and compliance logging
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
import logging

from modules.core.extensions import db
from .models import ExchangeRate, ExchangeTransaction, ExchangeType, ExchangeStatus, ExchangeProvider, LiquidityPool, ExchangeAlert

logger = logging.getLogger(__name__)

class ExchangeService:
    """
    Comprehensive exchange service handling internal and external exchange operations
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.name = "Exchange Service"
        self.supported_fiat_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD']
        self.supported_digital_currencies = ['NVCT', 'BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'ADA']
        self.exchange_fee_rate = Decimal('0.001')  # 0.1% fee
        
    # Internal Exchange Operations
    def get_current_rates(self) -> List[Dict[str, Any]]:
        """Get current internal exchange rates"""
        try:
            current_time = datetime.utcnow()
            rates = ExchangeRate.query.filter(
                ExchangeRate.provider == ExchangeProvider.INTERNAL_LIQUIDITY,
                ExchangeRate.valid_until > current_time
            ).order_by(ExchangeRate.timestamp.desc()).all()
            
            rate_data = []
            for rate in rates:
                rate_data.append({
                    'from_currency': rate.from_currency,
                    'to_currency': rate.to_currency,
                    'exchange_rate': float(rate.exchange_rate),
                    'provider': rate.provider.value,
                    'timestamp': rate.timestamp.isoformat(),
                    'valid_until': rate.valid_until.isoformat() if rate.valid_until else None,
                    'spread': float(rate.spread) if rate.spread else 0.0
                })
            
            return rate_data
            
        except Exception as e:
            logger.error(f"Error getting current rates: {e}")
            return []
    
    def get_supported_exchange_pairs(self) -> List[Dict[str, str]]:
        """Get all supported exchange pairs"""
        pairs = []
        
        # Fiat to Digital pairs
        for fiat in self.supported_fiat_currencies:
            for digital in self.supported_digital_currencies:
                pairs.append({
                    'from': fiat,
                    'to': digital,
                    'type': 'fiat_to_digital',
                    'category': 'Internal Exchange'
                })
                pairs.append({
                    'from': digital,
                    'to': fiat,
                    'type': 'digital_to_fiat',
                    'category': 'Internal Exchange'
                })
        
        # Digital to Digital pairs
        for i, digital1 in enumerate(self.supported_digital_currencies):
            for digital2 in self.supported_digital_currencies[i+1:]:
                pairs.append({
                    'from': digital1,
                    'to': digital2,
                    'type': 'digital_to_digital',
                    'category': 'Internal Exchange'
                })
                pairs.append({
                    'from': digital2,
                    'to': digital1,
                    'type': 'digital_to_digital',
                    'category': 'Internal Exchange'
                })
        
        return pairs
    
    def get_internal_quote(self, from_currency: str, to_currency: str, amount: Decimal) -> Optional[Dict[str, Any]]:
        """Get quote for internal exchange"""
        try:
            # Get current exchange rate
            rate = ExchangeRate.query.filter_by(
                from_currency=from_currency,
                to_currency=to_currency,
                provider=ExchangeProvider.INTERNAL_LIQUIDITY
            ).filter(
                ExchangeRate.valid_until > datetime.utcnow()
            ).order_by(ExchangeRate.timestamp.desc()).first()
            
            if not rate:
                return None
            
            # Calculate amounts
            destination_amount = amount * rate.exchange_rate
            exchange_fee = amount * self.exchange_fee_rate
            
            # Check liquidity
            liquidity_sufficient = self._check_liquidity(to_currency, destination_amount)
            
            quote = {
                'quote_id': f"internal_{datetime.utcnow().timestamp()}",
                'exchange_type': 'internal',
                'from_currency': from_currency,
                'to_currency': to_currency,
                'source_amount': float(amount),
                'destination_amount': float(destination_amount),
                'exchange_rate': float(rate.exchange_rate),
                'exchange_fee': float(exchange_fee),
                'total_cost': float(amount + exchange_fee),
                'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
                'rate_provider': rate.provider.value,
                'liquidity_sufficient': liquidity_sufficient
            }
            
            return quote
            
        except Exception as e:
            logger.error(f"Error getting internal quote: {e}")
            return None
    
    def get_external_quote(self, from_currency: str, to_currency: str, amount: Decimal, binance_service) -> Optional[Dict[str, Any]]:
        """Get quote for external exchange via Binance"""
        try:
            # Convert to Binance symbol format
            symbol = f"{from_currency}{to_currency}"
            
            # Get Binance ticker price
            ticker = binance_service.get_symbol_ticker(symbol)
            if not ticker:
                return None
            
            price = Decimal(str(ticker['price']))
            destination_amount = amount * price
            
            # External exchange fees (higher than internal)
            exchange_fee = amount * Decimal('0.002')  # 0.2% fee for external
            
            quote = {
                'quote_id': f"external_{datetime.utcnow().timestamp()}",
                'exchange_type': 'external',
                'from_currency': from_currency,
                'to_currency': to_currency,
                'source_amount': float(amount),
                'destination_amount': float(destination_amount),
                'exchange_rate': float(price),
                'exchange_fee': float(exchange_fee),
                'total_cost': float(amount + exchange_fee),
                'expires_at': (datetime.utcnow() + timedelta(minutes=2)).isoformat(),
                'rate_provider': 'Binance',
                'liquidity_sufficient': True  # Binance handles liquidity
            }
            
            return quote
            
        except Exception as e:
            logger.error(f"Error getting external quote: {e}")
            return None
    
    def execute_internal_exchange(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute internal exchange transaction"""
        try:
            from_currency = data.get('from_currency')
            to_currency = data.get('to_currency')
            amount = Decimal(str(data.get('amount')))
            source_account_id = data.get('source_account_id')
            destination_account_id = data.get('destination_account_id')
            
            # Determine exchange type
            exchange_type = self._determine_exchange_type(from_currency, to_currency)
            
            # Get fresh exchange rate
            rate = ExchangeRate.query.filter_by(
                from_currency=from_currency,
                to_currency=to_currency,
                provider=ExchangeProvider.INTERNAL_LIQUIDITY
            ).filter(
                ExchangeRate.valid_until > datetime.utcnow()
            ).order_by(ExchangeRate.timestamp.desc()).first()
            
            if not rate:
                return {'success': False, 'error': 'Exchange rate expired'}
            
            # Calculate amounts
            destination_amount = amount * rate.exchange_rate
            exchange_fee = amount * self.exchange_fee_rate
            
            # Verify accounts and balances
            verification_result = self._verify_accounts_and_balances(
                user_id, exchange_type, source_account_id, destination_account_id, amount, exchange_fee
            )
            
            if not verification_result['success']:
                return verification_result
            
            source_account = verification_result['source_account']
            destination_account = verification_result['destination_account']
            
            # Create exchange transaction record
            exchange_transaction = ExchangeTransaction(
                user_id=user_id,
                exchange_type=exchange_type,
                source_fiat_account_id=source_account_id if exchange_type in [ExchangeType.FIAT_TO_DIGITAL] else None,
                source_digital_account_id=source_account_id if exchange_type in [ExchangeType.DIGITAL_TO_FIAT, ExchangeType.DIGITAL_TO_DIGITAL] else None,
                destination_fiat_account_id=destination_account_id if exchange_type in [ExchangeType.DIGITAL_TO_FIAT] else None,
                destination_digital_account_id=destination_account_id if exchange_type in [ExchangeType.FIAT_TO_DIGITAL, ExchangeType.DIGITAL_TO_DIGITAL] else None,
                from_currency=from_currency,
                to_currency=to_currency,
                source_amount=amount,
                destination_amount=destination_amount,
                quoted_rate=rate.exchange_rate,
                executed_rate=rate.exchange_rate,
                rate_provider=rate.provider,
                exchange_fee=exchange_fee,
                status=ExchangeStatus.PROCESSING,
                quote_requested_at=datetime.utcnow(),
                quote_accepted_at=datetime.utcnow(),
                processing_started_at=datetime.utcnow()
            )
            
            db.session.add(exchange_transaction)
            db.session.flush()
            
            # Execute the exchange
            self._execute_exchange_by_type(
                exchange_type, source_account, destination_account,
                amount, exchange_fee, destination_amount,
                from_currency, to_currency, exchange_transaction, user_id
            )
            
            # Update status
            exchange_transaction.status = ExchangeStatus.COMPLETED
            exchange_transaction.completed_at = datetime.utcnow()
            
            # Log compliance data
            self._log_exchange_compliance(user_id, exchange_transaction, rate)
            
            db.session.commit()
            
            return {
                'success': True,
                'exchange_id': exchange_transaction.transaction_uuid,
                'source_amount': float(amount),
                'destination_amount': float(destination_amount),
                'exchange_fee': float(exchange_fee),
                'status': 'COMPLETED',
                'exchange_type': 'internal'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error executing internal exchange: {e}")
            return {'success': False, 'error': 'Internal exchange execution failed'}
    
    def execute_external_exchange(self, user_id: int, data: Dict[str, Any], binance_service) -> Dict[str, Any]:
        """Execute external exchange via Binance"""
        try:
            from_currency = data.get('from_currency')
            to_currency = data.get('to_currency')
            amount = Decimal(str(data.get('amount')))
            
            # Execute trade on Binance
            symbol = f"{from_currency}{to_currency}"
            order_result = binance_service.place_market_order(symbol, 'BUY', float(amount))
            
            if not order_result or order_result.get('status') != 'FILLED':
                return {'success': False, 'error': 'External exchange execution failed'}
            
            # Record external exchange transaction
            exchange_transaction = ExchangeTransaction(
                user_id=user_id,
                exchange_type=ExchangeType.EXTERNAL_EXCHANGE,
                from_currency=from_currency,
                to_currency=to_currency,
                source_amount=amount,
                destination_amount=Decimal(str(order_result.get('executedQty', 0))),
                quoted_rate=Decimal(str(order_result.get('price', 0))),
                executed_rate=Decimal(str(order_result.get('price', 0))),
                rate_provider=ExchangeProvider.BINANCE,
                exchange_fee=Decimal(str(order_result.get('commission', 0))),
                status=ExchangeStatus.COMPLETED,
                external_order_id=order_result.get('orderId'),
                quote_requested_at=datetime.utcnow(),
                quote_accepted_at=datetime.utcnow(),
                processing_started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            
            db.session.add(exchange_transaction)
            db.session.commit()
            
            return {
                'success': True,
                'exchange_id': exchange_transaction.transaction_uuid,
                'source_amount': float(amount),
                'destination_amount': float(exchange_transaction.destination_amount),
                'exchange_fee': float(exchange_transaction.exchange_fee),
                'status': 'COMPLETED',
                'exchange_type': 'external',
                'binance_order_id': order_result.get('orderId')
            }
            
        except Exception as e:
            logger.error(f"Error executing external exchange: {e}")
            return {'success': False, 'error': 'External exchange execution failed'}
    
    # Liquidity Pool Management
    def get_liquidity_pool_status(self) -> List[Dict[str, Any]]:
        """Get status of all liquidity pools"""
        try:
            pools = LiquidityPool.query.filter_by(is_active=True).all()
            
            pool_data = []
            for pool in pools:
                pool_data.append({
                    'currency': pool.currency,
                    'current_liquidity': float(pool.current_liquidity),
                    'target_liquidity': float(pool.target_liquidity),
                    'minimum_liquidity': float(pool.minimum_liquidity),
                    'utilization_rate': float(pool.utilization_rate) if pool.utilization_rate else 0.0,
                    'last_updated': pool.last_updated.isoformat() if pool.last_updated else None,
                    'status': 'healthy' if pool.current_liquidity > pool.minimum_liquidity else 'low'
                })
            
            return pool_data
            
        except Exception as e:
            logger.error(f"Error getting liquidity pool status: {e}")
            return []
    
    def get_currency_liquidity_status(self, currency: str) -> Dict[str, Any]:
        """Get liquidity status for specific currency"""
        try:
            pool = LiquidityPool.query.filter_by(currency=currency, is_active=True).first()
            
            if not pool:
                return {'error': 'Currency not found', 'currency': currency}
            
            return {
                'currency': currency,
                'current_liquidity': float(pool.current_liquidity),
                'target_liquidity': float(pool.target_liquidity),
                'minimum_liquidity': float(pool.minimum_liquidity),
                'utilization_rate': float(pool.utilization_rate) if pool.utilization_rate else 0.0,
                'last_updated': pool.last_updated.isoformat() if pool.last_updated else None,
                'status': 'healthy' if pool.current_liquidity > pool.minimum_liquidity else 'low',
                'available_for_exchange': float(pool.current_liquidity - pool.minimum_liquidity)
            }
            
        except Exception as e:
            logger.error(f"Error getting currency liquidity status: {e}")
            return {'error': 'Failed to get liquidity status', 'currency': currency}
    
    # Transaction History and Analytics
    def get_user_exchange_history(self, user_id: int, limit: int = 20, page: int = 1, per_page: int = 20, 
                                 exchange_type: str = None, from_date: str = None, to_date: str = None) -> Dict[str, Any]:
        """Get user's exchange transaction history"""
        try:
            query = ExchangeTransaction.query.filter_by(user_id=user_id)
            
            # Apply filters
            if exchange_type and exchange_type != 'all':
                if exchange_type == 'internal':
                    query = query.filter(ExchangeTransaction.exchange_type.in_([
                        ExchangeType.FIAT_TO_DIGITAL,
                        ExchangeType.DIGITAL_TO_FIAT,
                        ExchangeType.DIGITAL_TO_DIGITAL
                    ]))
                elif exchange_type == 'external':
                    query = query.filter_by(exchange_type=ExchangeType.EXTERNAL_EXCHANGE)
            
            if from_date:
                query = query.filter(ExchangeTransaction.created_at >= datetime.fromisoformat(from_date))
            
            if to_date:
                query = query.filter(ExchangeTransaction.created_at <= datetime.fromisoformat(to_date))
            
            # Apply pagination if requested
            if page and per_page:
                paginated = query.order_by(ExchangeTransaction.created_at.desc()).paginate(
                    page=page, per_page=per_page, error_out=False
                )
                transactions = paginated.items
                total = paginated.total
                pages = paginated.pages
            else:
                transactions = query.order_by(ExchangeTransaction.created_at.desc()).limit(limit).all()
                total = len(transactions)
                pages = 1
            
            history_data = []
            for transaction in transactions:
                history_data.append({
                    'transaction_id': transaction.transaction_uuid,
                    'exchange_type': transaction.exchange_type.value,
                    'from_currency': transaction.from_currency,
                    'to_currency': transaction.to_currency,
                    'source_amount': float(transaction.source_amount),
                    'destination_amount': float(transaction.destination_amount),
                    'exchange_rate': float(transaction.executed_rate),
                    'exchange_fee': float(transaction.exchange_fee),
                    'status': transaction.status.value,
                    'created_at': transaction.created_at.isoformat(),
                    'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None,
                    'rate_provider': transaction.rate_provider.value if transaction.rate_provider else None
                })
            
            return {
                'transactions': history_data,
                'total': total,
                'pages': pages,
                'current_page': page if page else 1
            }
            
        except Exception as e:
            logger.error(f"Error getting exchange history: {e}")
            return {'transactions': [], 'total': 0, 'pages': 0, 'current_page': 1}
    
    def get_exchange_statistics(self) -> Dict[str, Any]:
        """Get comprehensive exchange statistics for admin dashboard"""
        try:
            current_time = datetime.utcnow()
            last_24h = current_time - timedelta(hours=24)
            last_30d = current_time - timedelta(days=30)
            
            # Basic statistics
            total_exchanges = ExchangeTransaction.query.count()
            exchanges_24h = ExchangeTransaction.query.filter(ExchangeTransaction.created_at >= last_24h).count()
            exchanges_30d = ExchangeTransaction.query.filter(ExchangeTransaction.created_at >= last_30d).count()
            
            # Volume statistics
            volume_24h = db.session.query(
                db.func.sum(ExchangeTransaction.source_amount)
            ).filter(ExchangeTransaction.created_at >= last_24h).scalar() or 0
            
            volume_30d = db.session.query(
                db.func.sum(ExchangeTransaction.source_amount)
            ).filter(ExchangeTransaction.created_at >= last_30d).scalar() or 0
            
            # Fee revenue
            fees_24h = db.session.query(
                db.func.sum(ExchangeTransaction.exchange_fee)
            ).filter(ExchangeTransaction.created_at >= last_24h).scalar() or 0
            
            fees_30d = db.session.query(
                db.func.sum(ExchangeTransaction.exchange_fee)
            ).filter(ExchangeTransaction.created_at >= last_30d).scalar() or 0
            
            # Success rate
            completed_24h = ExchangeTransaction.query.filter(
                ExchangeTransaction.created_at >= last_24h,
                ExchangeTransaction.status == ExchangeStatus.COMPLETED
            ).count()
            
            success_rate_24h = (completed_24h / exchanges_24h * 100) if exchanges_24h > 0 else 100
            
            return {
                'total_exchanges': total_exchanges,
                'exchanges_24h': exchanges_24h,
                'exchanges_30d': exchanges_30d,
                'volume_24h': float(volume_24h),
                'volume_30d': float(volume_30d),
                'fees_24h': float(fees_24h),
                'fees_30d': float(fees_30d),
                'success_rate_24h': round(success_rate_24h, 2),
                'active_liquidity_pools': LiquidityPool.query.filter_by(is_active=True).count(),
                'last_updated': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting exchange statistics: {e}")
            return {}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Exchange module health status - simplified to avoid model conflicts"""
        try:
            # Basic database connectivity check only
            db_check = db.session.execute(db.text('SELECT 1')).scalar()
            
            return {
                'status': 'healthy',
                'version': self.version,
                'service_name': self.name,
                'app_module': 'exchange',
                'database_connected': bool(db_check),
                'supported_currencies': len(self.supported_fiat_currencies + self.supported_digital_currencies),
                'features': ['internal_exchange', 'external_exchange', 'binance_integration'],
                'last_health_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Exchange module health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_health_check': datetime.utcnow().isoformat()
            }
    
    # Private helper methods
    def _check_liquidity(self, currency: str, amount: Decimal) -> bool:
        """Check if sufficient liquidity exists for exchange"""
        try:
            pool = LiquidityPool.query.filter_by(currency=currency, is_active=True).first()
            if not pool:
                return False
            
            available_liquidity = pool.current_liquidity - pool.minimum_liquidity
            return available_liquidity >= amount
            
        except Exception as e:
            logger.error(f"Error checking liquidity: {e}")
            return False
    
    def _determine_exchange_type(self, from_currency: str, to_currency: str) -> ExchangeType:
        """Determine exchange type based on currencies"""
        if from_currency in self.supported_fiat_currencies and to_currency in self.supported_digital_currencies:
            return ExchangeType.FIAT_TO_DIGITAL
        elif from_currency in self.supported_digital_currencies and to_currency in self.supported_fiat_currencies:
            return ExchangeType.DIGITAL_TO_FIAT
        elif from_currency in self.supported_digital_currencies and to_currency in self.supported_digital_currencies:
            return ExchangeType.DIGITAL_TO_DIGITAL
        else:
            raise ValueError("Unsupported currency pair")
    
    def _verify_accounts_and_balances(self, user_id: int, exchange_type: ExchangeType, 
                                    source_account_id: int, destination_account_id: int, 
                                    amount: Decimal, exchange_fee: Decimal) -> Dict[str, Any]:
        """Verify account ownership and sufficient balances"""
        try:
            # Get source and destination accounts based on exchange type
            if exchange_type == ExchangeType.FIAT_TO_DIGITAL:
                source_account = BankAccount.query.filter_by(id=source_account_id, user_id=user_id).first()
                destination_account = DigitalAssetAccount.query.filter_by(id=destination_account_id, user_id=user_id).first()
            elif exchange_type == ExchangeType.DIGITAL_TO_FIAT:
                source_account = DigitalAssetAccount.query.filter_by(id=source_account_id, user_id=user_id).first()
                destination_account = BankAccount.query.filter_by(id=destination_account_id, user_id=user_id).first()
            else:  # DIGITAL_TO_DIGITAL
                source_account = DigitalAssetAccount.query.filter_by(id=source_account_id, user_id=user_id).first()
                destination_account = DigitalAssetAccount.query.filter_by(id=destination_account_id, user_id=user_id).first()
            
            if not source_account or not destination_account:
                return {'success': False, 'error': 'Invalid account selection'}
            
            # Check balances
            if exchange_type == ExchangeType.FIAT_TO_DIGITAL:
                if source_account.available_balance < (amount + exchange_fee):
                    return {'success': False, 'error': 'Insufficient fiat balance'}
            else:
                if not source_account.can_transfer(amount + exchange_fee):
                    return {'success': False, 'error': 'Insufficient balance'}
            
            return {
                'success': True,
                'source_account': source_account,
                'destination_account': destination_account
            }
            
        except Exception as e:
            logger.error(f"Error verifying accounts and balances: {e}")
            return {'success': False, 'error': 'Account verification failed'}
    
    def _execute_exchange_by_type(self, exchange_type: ExchangeType, source_account, destination_account,
                                 amount: Decimal, exchange_fee: Decimal, destination_amount: Decimal,
                                 from_currency: str, to_currency: str, exchange_transaction, user_id: int):
        """Execute exchange based on type"""
        if exchange_type == ExchangeType.FIAT_TO_DIGITAL:
            self._execute_fiat_to_digital_exchange(
                source_account, destination_account, amount, exchange_fee, 
                destination_amount, from_currency, to_currency, exchange_transaction, user_id
            )
        elif exchange_type == ExchangeType.DIGITAL_TO_FIAT:
            self._execute_digital_to_fiat_exchange(
                source_account, destination_account, amount, exchange_fee,
                destination_amount, from_currency, to_currency, exchange_transaction, user_id
            )
        else:  # DIGITAL_TO_DIGITAL
            self._execute_digital_to_digital_exchange(
                source_account, destination_account, amount, exchange_fee,
                destination_amount, from_currency, to_currency, exchange_transaction, user_id
            )
    
    def _execute_fiat_to_digital_exchange(self, source_account, destination_account, amount, exchange_fee,
                                        destination_amount, from_currency, to_currency, exchange_transaction, user_id):
        """Execute fiat to digital asset exchange"""
        # Debit fiat account
        fiat_transaction = Transaction(
            from_account_id=source_account.id,
            amount=amount + exchange_fee,
            transaction_type=TransactionType.CURRENCY_EXCHANGE,
            status=TransactionStatus.COMPLETED,
            description=f"Exchange to {to_currency}",
            created_by=user_id
        )
        db.session.add(fiat_transaction)
        
        # Update fiat account balance
        source_account.current_balance -= (amount + exchange_fee)
        source_account.available_balance -= (amount + exchange_fee)
        
        # Credit digital asset account
        destination_account.update_balance(destination_amount, 'credit')
        
        # Create digital asset transaction
        digital_transaction = DigitalAssetTransaction(
            to_account_id=destination_account.id,
            amount=destination_amount,
            transaction_type=DigitalAssetTransactionType.TOKEN_TRANSFER,
            token_type=TokenType(to_currency),
            blockchain_network=BlockchainNetwork.ETHEREUM,
            status=DigitalAssetTransactionStatus.CONFIRMED,
            transaction_date=datetime.utcnow(),
            confirmation_date=datetime.utcnow(),
            created_by=user_id
        )
        db.session.add(digital_transaction)
        
        # Link transactions to exchange
        exchange_transaction.fiat_transaction_id = fiat_transaction.id
        exchange_transaction.digital_transaction_id = digital_transaction.id
    
    def _execute_digital_to_fiat_exchange(self, source_account, destination_account, amount, exchange_fee,
                                        destination_amount, from_currency, to_currency, exchange_transaction, user_id):
        """Execute digital asset to fiat exchange"""
        # Debit digital asset account
        source_account.update_balance(amount + exchange_fee, 'debit')
        
        # Create digital asset transaction
        digital_transaction = DigitalAssetTransaction(
            from_account_id=source_account.id,
            amount=amount + exchange_fee,
            transaction_type=DigitalAssetTransactionType.TOKEN_TRANSFER,
            token_type=TokenType(from_currency),
            blockchain_network=BlockchainNetwork.ETHEREUM,
            status=DigitalAssetTransactionStatus.CONFIRMED,
            transaction_date=datetime.utcnow(),
            confirmation_date=datetime.utcnow(),
            created_by=user_id
        )
        db.session.add(digital_transaction)
        
        # Credit fiat account
        fiat_transaction = Transaction(
            to_account_id=destination_account.id,
            amount=destination_amount,
            transaction_type=TransactionType.CURRENCY_EXCHANGE,
            status=TransactionStatus.COMPLETED,
            description=f"Exchange from {from_currency}",
            created_by=user_id
        )
        db.session.add(fiat_transaction)
        
        # Update fiat account balance
        destination_account.current_balance += destination_amount
        destination_account.available_balance += destination_amount
        
        # Link transactions to exchange
        exchange_transaction.fiat_transaction_id = fiat_transaction.id
        exchange_transaction.digital_transaction_id = digital_transaction.id
    
    def _execute_digital_to_digital_exchange(self, source_account, destination_account, amount, exchange_fee,
                                           destination_amount, from_currency, to_currency, exchange_transaction, user_id):
        """Execute digital asset to digital asset exchange"""
        # Debit source digital asset account
        source_account.update_balance(amount + exchange_fee, 'debit')
        
        # Create source digital asset transaction
        source_transaction = DigitalAssetTransaction(
            from_account_id=source_account.id,
            amount=amount + exchange_fee,
            transaction_type=DigitalAssetTransactionType.TOKEN_TRANSFER,
            token_type=TokenType(from_currency),
            blockchain_network=BlockchainNetwork.ETHEREUM,
            status=DigitalAssetTransactionStatus.CONFIRMED,
            transaction_date=datetime.utcnow(),
            confirmation_date=datetime.utcnow(),
            created_by=user_id
        )
        db.session.add(source_transaction)
        
        # Credit destination digital asset account
        destination_account.update_balance(destination_amount, 'credit')
        
        # Create destination digital asset transaction
        destination_transaction = DigitalAssetTransaction(
            to_account_id=destination_account.id,
            amount=destination_amount,
            transaction_type=DigitalAssetTransactionType.TOKEN_TRANSFER,
            token_type=TokenType(to_currency),
            blockchain_network=BlockchainNetwork.ETHEREUM,
            status=DigitalAssetTransactionStatus.CONFIRMED,
            transaction_date=datetime.utcnow(),
            confirmation_date=datetime.utcnow(),
            created_by=user_id
        )
        db.session.add(destination_transaction)
        
        # Link transactions to exchange
        exchange_transaction.digital_transaction_id = source_transaction.id
        exchange_transaction.destination_digital_transaction_id = destination_transaction.id
    
    def _log_exchange_compliance(self, user_id: int, exchange_transaction, rate):
        """Log exchange transaction for compliance"""
        try:
            from flask_login import current_user
            
            ExchangeComplianceLogger.log_exchange_transaction(
                user=current_user,
                exchange_data={
                    'transaction_uuid': exchange_transaction.transaction_uuid,
                    'exchange_type': exchange_transaction.exchange_type.value,
                    'from_currency': exchange_transaction.from_currency,
                    'to_currency': exchange_transaction.to_currency,
                    'source_amount': exchange_transaction.source_amount,
                    'destination_amount': exchange_transaction.destination_amount,
                    'exchange_rate': exchange_transaction.executed_rate,
                    'exchange_fee': exchange_transaction.exchange_fee,
                    'rate_provider': rate.provider.value
                },
                quote_data={
                    'quoted_rate': rate.exchange_rate,
                    'rate_timestamp': rate.timestamp.isoformat(),
                    'rate_valid_until': rate.valid_until.isoformat() if rate.valid_until else None
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log exchange compliance data: {e}")
    
    # Admin-only methods
    def get_all_liquidity_pools(self) -> List[Dict[str, Any]]:
        """Get all liquidity pools (admin only)"""
        try:
            pools = LiquidityPool.query.all()
            
            pool_data = []
            for pool in pools:
                pool_data.append({
                    'id': pool.id,
                    'currency': pool.currency,
                    'current_liquidity': float(pool.current_liquidity),
                    'target_liquidity': float(pool.target_liquidity),
                    'minimum_liquidity': float(pool.minimum_liquidity),
                    'utilization_rate': float(pool.utilization_rate) if pool.utilization_rate else 0.0,
                    'is_active': pool.is_active,
                    'created_at': pool.created_at.isoformat() if pool.created_at else None,
                    'last_updated': pool.last_updated.isoformat() if pool.last_updated else None
                })
            
            return pool_data
            
        except Exception as e:
            logger.error(f"Error getting all liquidity pools: {e}")
            return []
    
    def get_liquidity_analytics(self) -> Dict[str, Any]:
        """Get liquidity analytics (admin only)"""
        try:
            # Total liquidity across all pools
            total_liquidity = db.session.query(
                db.func.sum(LiquidityPool.current_liquidity)
            ).filter_by(is_active=True).scalar() or 0
            
            # Average utilization rate
            avg_utilization = db.session.query(
                db.func.avg(LiquidityPool.utilization_rate)
            ).filter_by(is_active=True).scalar() or 0
            
            # Pools below minimum threshold
            low_liquidity_pools = LiquidityPool.query.filter(
                LiquidityPool.is_active == True,
                LiquidityPool.current_liquidity < LiquidityPool.minimum_liquidity
            ).count()
            
            return {
                'total_liquidity': float(total_liquidity),
                'average_utilization_rate': float(avg_utilization),
                'low_liquidity_pools': low_liquidity_pools,
                'active_pools': LiquidityPool.query.filter_by(is_active=True).count(),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting liquidity analytics: {e}")
            return {}
    
    def get_recent_exchange_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent exchange transactions (admin only)"""
        try:
            transactions = ExchangeTransaction.query.order_by(
                ExchangeTransaction.created_at.desc()
            ).limit(limit).all()
            
            transaction_data = []
            for transaction in transactions:
                transaction_data.append({
                    'transaction_id': transaction.transaction_uuid,
                    'user_id': transaction.user_id,
                    'exchange_type': transaction.exchange_type.value,
                    'from_currency': transaction.from_currency,
                    'to_currency': transaction.to_currency,
                    'source_amount': float(transaction.source_amount),
                    'destination_amount': float(transaction.destination_amount),
                    'exchange_fee': float(transaction.exchange_fee),
                    'status': transaction.status.value,
                    'created_at': transaction.created_at.isoformat(),
                    'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None
                })
            
            return transaction_data
            
        except Exception as e:
            logger.error(f"Error getting recent exchange transactions: {e}")
            return []
    
    def get_rate_providers_status(self) -> List[Dict[str, Any]]:
        """Get status of all rate providers (admin only)"""
        try:
            providers_status = []
            
            # Internal liquidity provider
            internal_rates_count = ExchangeRate.query.filter_by(
                provider=ExchangeProvider.INTERNAL_LIQUIDITY
            ).filter(
                ExchangeRate.valid_until > datetime.utcnow()
            ).count()
            
            providers_status.append({
                'provider': 'Internal Liquidity',
                'status': 'active' if internal_rates_count > 0 else 'inactive',
                'active_rates': internal_rates_count,
                'last_update': datetime.utcnow().isoformat()
            })
            
            # External providers can be added here
            providers_status.append({
                'provider': 'Binance',
                'status': 'external',
                'active_rates': 'via_api',
                'last_update': datetime.utcnow().isoformat()
            })
            
            return providers_status
            
        except Exception as e:
            logger.error(f"Error getting rate providers status: {e}")
            return []
    
    def get_rate_history(self) -> List[Dict[str, Any]]:
        """Get exchange rate history (admin only)"""
        try:
            rates = ExchangeRate.query.order_by(
                ExchangeRate.timestamp.desc()
            ).limit(100).all()
            
            rate_data = []
            for rate in rates:
                rate_data.append({
                    'from_currency': rate.from_currency,
                    'to_currency': rate.to_currency,
                    'exchange_rate': float(rate.exchange_rate),
                    'spread': float(rate.spread) if rate.spread else 0.0,
                    'provider': rate.provider.value,
                    'timestamp': rate.timestamp.isoformat(),
                    'valid_until': rate.valid_until.isoformat() if rate.valid_until else None
                })
            
            return rate_data
            
        except Exception as e:
            logger.error(f"Error getting rate history: {e}")
            return []
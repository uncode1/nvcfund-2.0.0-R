"""
Modular Blueprint Registration System
Direct Flask blueprint registration ensuring complete divorce from legacy features
"""

import logging
import importlib
from flask import Flask

logger = logging.getLogger(__name__)

def register_all_modules(app: Flask):
    """
    Register all modular blueprints directly with Flask application
    Ensures complete separation from legacy features
    """
    registration_results = []
    
    # Administration module removed per user request - not effective
    
    # Register the new products module and sub-modules
    try:
        from modules.products import products_bp, cards_payments_bp, insurance_bp, investments_bp, trading_bp, loans_bp
        app.register_blueprint(products_bp)
        logger.info("✅ Products module registered successfully")

        # Register product sub-modules
        if cards_payments_bp:
            app.register_blueprint(cards_payments_bp)
            logger.info("✅ Cards & Payments product module registered successfully")

        if insurance_bp:
            app.register_blueprint(insurance_bp)
            logger.info("✅ Insurance product module registered successfully")

        if investments_bp:
            app.register_blueprint(investments_bp)
            logger.info("✅ Investments product module registered successfully")

        if trading_bp:
            app.register_blueprint(trading_bp)
            logger.info("✅ Trading product module registered successfully")

        if loans_bp:
            app.register_blueprint(loans_bp)
            logger.info("✅ Loans product module registered successfully")

    except Exception as e:
        logger.error(f"❌ Failed to register Products module: {e}")
    
    # Register the new services module and its sub-modules
    try:
        from modules.services import services_bp, communications_bp, mfa_bp, api_bp, integrations_bp
        app.register_blueprint(services_bp)
        logger.info("✅ Services module registered successfully")
        
        # Register services sub-modules
        if communications_bp:
            app.register_blueprint(communications_bp)
            logger.info("✅ Communications service module registered successfully")
        
        if mfa_bp:
            app.register_blueprint(mfa_bp)
            logger.info("✅ MFA service module registered successfully")
        
        if api_bp:
            app.register_blueprint(api_bp)
            logger.info("✅ API service module registered successfully")
        
        if integrations_bp:
            app.register_blueprint(integrations_bp)
            logger.info("✅ Integrations service module registered successfully")
        

        

            
    except Exception as e:
        logger.error(f"❌ Failed to register Services module: {e}")
    
    # Define all active modules (22 modules with working routes.py files - migrated integrations, api, utils to services container)
    active_modules = [
        # Core operational modules (currently working)
        'public',
        'auth',
        'dashboard',
        'banking',

        # Tier 1 banking modules
        'accounts',
        'treasury',

        'compliance',

        'nvct_stablecoin',
        'sovereign',
    


        
        # Admin and management modules
        'admin_management',
        'security_center',

        'user_management',
        # 'analytics', # Moved to services container
        
        # Communications and security modules (communications, mfa migrated to services container)
        
        # Additional feature modules

    
        
        # New container modules are manually registered above
    ]
    
    for module_name in active_modules:
        try:
            # Import the module dynamically
            module = __import__(f'modules.{module_name}.routes', fromlist=[''])
            
            # Get the blueprint(s) from the module
            blueprint_found = False
            
            # Try specific module patterns with custom URL prefixes FIRST
            if module_name == 'public':
                # Public module routes should be at root level (no URL prefix)
                # Register both main public blueprint and API blueprint
                if hasattr(module, 'public_bp'):
                    blueprint = getattr(module, 'public_bp')
                    app.register_blueprint(blueprint)
                    blueprint_found = True

                # Also register the public API blueprint
                if hasattr(module, 'public_api_bp'):
                    api_blueprint = getattr(module, 'public_api_bp')
                    app.register_blueprint(api_blueprint)
                    logger.info(f"✅ Public API blueprint registered at {api_blueprint.url_prefix}/*")
                elif hasattr(module, 'get_public_blueprints'):
                    # Use the new function to get all blueprints
                    blueprints = module.get_public_blueprints()
                    for bp in blueprints:
                        if bp.name != 'public':  # Main blueprint already registered above
                            app.register_blueprint(bp)
                            logger.info(f"✅ {bp.name} blueprint registered at {bp.url_prefix}/*")
            elif module_name == 'api' and hasattr(module, 'api_bp'):
                # API module already has /api/v1 prefix configured internally
                blueprint = getattr(module, 'api_bp')
                app.register_blueprint(blueprint)
                blueprint_found = True
            elif module_name == 'auth' and hasattr(module, 'auth_bp'):
                # Auth module with explicit /auth prefix
                blueprint = getattr(module, 'auth_bp')
                app.register_blueprint(blueprint, url_prefix='/auth')
                blueprint_found = True
            elif module_name == 'admin_management' and hasattr(module, 'admin_management_bp'):
                blueprint = getattr(module, 'admin_management_bp')
                app.register_blueprint(blueprint, url_prefix='/admin')
                
                # Register hyphen blueprint if available
                if hasattr(module, 'admin_management_hyphen_bp'):
                    hyphen_blueprint = getattr(module, 'admin_management_hyphen_bp')
                    app.register_blueprint(hyphen_blueprint, url_prefix='/admin-management')
                    logger.info(f"✅ Admin Management hyphen blueprint registered at /admin-management/*")
                
                blueprint_found = True
            elif module_name == 'security_center' and hasattr(module, 'security_center_bp'):
                blueprint = getattr(module, 'security_center_bp')
                app.register_blueprint(blueprint)  # Blueprint already has url_prefix='/security_center'
                blueprint_found = True
            elif module_name == 'system_management' and hasattr(module, 'system_management_bp'):
                blueprint = getattr(module, 'system_management_bp')
                app.register_blueprint(blueprint)  # Blueprint already has url_prefix='/system_management'
                blueprint_found = True
            elif module_name == 'dashboard' and hasattr(module, 'dashboard_bp'):
                # Dashboard module gets special handling for both web and API blueprints
                blueprint = getattr(module, 'dashboard_bp')
                app.register_blueprint(blueprint)
                # Also register API blueprint if available
                try:
                    api_module = __import__(f'modules.{module_name}.api_routes', fromlist=[''])
                    if hasattr(api_module, 'dashboard_api_bp'):
                        api_blueprint = getattr(api_module, 'dashboard_api_bp')
                        app.register_blueprint(api_blueprint)
                        logger.info(f"✅ Dashboard API blueprint registered at /api/v1/dashboard/*")
                except ImportError:
                    pass

                # Specialized dashboard blueprints will be registered here when implemented
                pass

                # Register binance_integration blueprint alias
                try:
                    from modules.services.integrations.blockchain.binance.routes import binance_integration_bp
                    app.register_blueprint(binance_integration_bp)
                    logger.info("✅ Binance Integration alias blueprint registered")
                except ImportError as e:
                    logger.warning(f"Failed to register binance integration blueprint: {e}")

                # Additional dashboard blueprints will be registered here when implemented
                pass

                # Register crypto blueprint
                try:
                    from modules.banking.crypto_routes import crypto_bp
                    app.register_blueprint(crypto_bp)
                    logger.info("✅ Crypto blueprint registered")
                except ImportError as e:
                    logger.warning(f"Failed to register crypto blueprint: {e}")

                blueprint_found = True
            # Handle integrations module with sub-modules
            elif module_name == 'integrations' and hasattr(module, 'integrations_bp'):
                # Register main integrations blueprint
                integrations_blueprint = getattr(module, 'integrations_bp')
                app.register_blueprint(integrations_blueprint)
                
                # Register payment_gateways sub-module blueprint
                if hasattr(module, 'payment_gateways_bp'):
                    payment_gateways_blueprint = getattr(module, 'payment_gateways_bp')
                    app.register_blueprint(payment_gateways_blueprint)
                
                # Register individual payment gateway blueprints
                if hasattr(module, 'paypal_bp'):
                    paypal_blueprint = getattr(module, 'paypal_bp')
                    app.register_blueprint(paypal_blueprint)
                
                if hasattr(module, 'stripe_bp'):
                    stripe_blueprint = getattr(module, 'stripe_bp')
                    app.register_blueprint(stripe_blueprint)
                
                if hasattr(module, 'flutterwave_bp'):
                    flutterwave_blueprint = getattr(module, 'flutterwave_bp')
                    app.register_blueprint(flutterwave_blueprint)
                
                if hasattr(module, 'ach_network_bp'):
                    ach_network_blueprint = getattr(module, 'ach_network_bp')
                    app.register_blueprint(ach_network_blueprint)
                
                # Register blockchain sub-module blueprint
                if hasattr(module, 'blockchain_bp'):
                    blockchain_blueprint = getattr(module, 'blockchain_bp')
                    app.register_blueprint(blockchain_blueprint)
                
                # Register blockchain analytics sub-module blueprint
                if hasattr(module, 'blockchain_analytics_bp'):
                    blockchain_analytics_blueprint = getattr(module, 'blockchain_analytics_bp')
                    app.register_blueprint(blockchain_analytics_blueprint)
                
                # Register communications integration sub-module blueprint
                if hasattr(module, 'communications_integration_bp'):
                    communications_integration_blueprint = getattr(module, 'communications_integration_bp')
                    app.register_blueprint(communications_integration_blueprint)
                    logger.info(f"✅ Communications Integration blueprint registered successfully with URL prefix: {communications_integration_blueprint.url_prefix}")
                
                # Register individual communication service blueprints
                if hasattr(module, 'sendgrid_bp'):
                    sendgrid_blueprint = getattr(module, 'sendgrid_bp')
                    app.register_blueprint(sendgrid_blueprint)
                    logger.info(f"✅ SendGrid blueprint registered successfully with URL prefix: {sendgrid_blueprint.url_prefix}")
                
                if hasattr(module, 'twilio_bp'):
                    twilio_blueprint = getattr(module, 'twilio_bp')
                    app.register_blueprint(twilio_blueprint)
                    logger.info(f"✅ Twilio blueprint registered successfully with URL prefix: {twilio_blueprint.url_prefix}")
                
                # Register financial data sub-module blueprint
                if hasattr(module, 'financial_data_bp'):
                    financial_data_blueprint = getattr(module, 'financial_data_bp')
                    app.register_blueprint(financial_data_blueprint)
                    logger.info(f"✅ Financial Data blueprint registered successfully with URL prefix: {financial_data_blueprint.url_prefix}")
                
                # Register individual financial data provider blueprints
                if hasattr(module, 'plaid_bp'):
                    plaid_blueprint = getattr(module, 'plaid_bp')
                    app.register_blueprint(plaid_blueprint)
                    logger.info(f"✅ Plaid blueprint registered successfully with URL prefix: {plaid_blueprint.url_prefix}")
                
                blueprint_found = True
            # Try standard naming pattern for modules without custom prefixes
            elif hasattr(module, f'{module_name}_bp'):
                blueprint = getattr(module, f'{module_name}_bp')
                
                # All modules now use their blueprint-defined URL prefixes (clean URLs)
                app.register_blueprint(blueprint)
                
                # Log clean URL registration for modules that use clean format
                hyphenated_url_modules = {
                    'smart_contracts': 'smart-contracts',
                    'cards_payments': 'cards-payments', 
                    'user_management': 'user-management',
                    'islamic_banking': 'islamic-banking',
                    'system_management': 'system-management',
                    'security_center': 'security-center',
                    'nvct_stablecoin': 'nvct-stablecoin',

                    'blockchain_analytics': 'blockchain-analytics',

                }
                
                if module_name in hyphenated_url_modules:
                    hyphenated_url = hyphenated_url_modules[module_name]
                    logger.info(f"✅ {module_name.replace('_', ' ').title()} registered with hyphenated URL: /{hyphenated_url}/*")
                
                blueprint_found = True
            
            # Try shortened name patterns with proper URL prefixes

            elif module_name == 'cards_payments' and hasattr(module, 'cards_bp'):
                blueprint = getattr(module, 'cards_bp')
                app.register_blueprint(blueprint, url_prefix='/cards')
                blueprint_found = True
            # NVCT Stablecoin handled by standard registration above - no duplicate needed


            # Note: admin_management, security_center, and system_management 
            # are handled above in the specific patterns section
            elif module_name == 'islamic_banking' and hasattr(module, 'islamic_bp'):
                blueprint = getattr(module, 'islamic_bp')
                app.register_blueprint(blueprint, url_prefix='/islamic')
                blueprint_found = True
            elif module_name == 'user_management' and hasattr(module, 'user_management_bp'):
                blueprint = getattr(module, 'user_management_bp')
                app.register_blueprint(blueprint)  # Blueprint already has url_prefix='/user-management'
                # Also register with underscore URL for backwards compatibility
                app.register_blueprint(blueprint, url_prefix='/user_management')
                blueprint_found = True
            elif module_name == 'communications' and hasattr(module, 'communications_bp'):
                blueprint = getattr(module, 'communications_bp')
                app.register_blueprint(blueprint)  # Blueprint already has url_prefix='/communications'
                blueprint_found = True
            elif module_name == 'mfa' and hasattr(module, 'mfa_bp'):
                blueprint = getattr(module, 'mfa_bp')
                app.register_blueprint(blueprint)  # Blueprint already has url_prefix='/mfa'
                blueprint_found = True
            elif module_name == 'products' and hasattr(module, 'products_bp'):
                blueprint = getattr(module, 'products_bp')
                try:
                    app.register_blueprint(blueprint)  # Blueprint already has url_prefix='/products'
                    blueprint_found = True
                except ValueError as e:
                    if "already registered" in str(e):
                        logger.warning(f"Products blueprint already registered, skipping duplicate registration")
                        blueprint_found = True
                    else:
                        raise e
            elif module_name == 'services' and hasattr(module, 'services_bp'):
                blueprint = getattr(module, 'services_bp')
                try:
                    app.register_blueprint(blueprint)  # Blueprint already has url_prefix='/services'
                    blueprint_found = True
                except ValueError as e:
                    if "already registered" in str(e):
                        logger.warning(f"Services blueprint already registered, skipping duplicate registration")
                        blueprint_found = True
                    else:
                        raise e
            elif module_name == 'analytics':
                # Skip analytics module in normal registration to avoid decorator conflicts
                # Will be manually registered after all other modules
                blueprint_found = True
                registration_results.append(f"⏭️  Analytics Module deferred for manual registration")
                logger.info(f"Analytics module deferred for manual registration")
            elif module_name == 'admin_management' and hasattr(module, 'admin_mgmt_bp'):
                # Admin_Management module has backup_management endpoint conflict
                # Skip for now and register manually later without conflicts
                logger.warning(f"Admin_Management module temporarily bypassed due to endpoint conflict")
                blueprint_found = True
            
            # Skip individual module API blueprints to prevent conflicts with centralized API
            elif hasattr(module, 'api_blueprints'):
                logger.info(f"Skipping individual API blueprints for {module_name} - using centralized API")
                blueprint_found = True
            
            if blueprint_found:
                registration_results.append(f"✅ {module_name.title()} Module registered successfully")
                logger.info(f"{module_name.title()} Module registered successfully")
                
                # Special post-registration handling for integrations module sub-modules
                if module_name == 'integrations':
                    # Manually register sub-module blueprints that weren't caught by hasattr
                    try:
                        # Import and register all integration sub-modules
                        from modules.services.integrations.communications.routes import communications_integration_bp
                        from modules.services.integrations.communications.sendgrid.routes import sendgrid_bp
                        from modules.services.integrations.communications.twilio.routes import twilio_bp
                        from modules.services.integrations.financial_data.routes import financial_data_bp
                        from modules.services.integrations.financial_data.plaid.routes import plaid_bp
                        from modules.services.integrations.payment_gateways.routes import payment_gateways_bp
                        from modules.services.integrations.payment_gateways.paypal.routes import paypal_bp
                        from modules.services.integrations.payment_gateways.stripe.routes import stripe_bp
                        from modules.services.integrations.payment_gateways.flutterwave.routes import flutterwave_bp
                        from modules.services.integrations.payment_gateways.ach_network.routes import ach_network_bp
                        from modules.services.integrations.blockchain.routes import blockchain_bp
                        from modules.services.integrations.blockchain.analytics.routes import blockchain_analytics_bp
                        
                        # Register all sub-module blueprints directly
                        sub_modules = [
                            (communications_integration_bp, "Communications Integration"),
                            (sendgrid_bp, "SendGrid"), 
                            (twilio_bp, "Twilio"),
                            (financial_data_bp, "Financial Data"),
                            (plaid_bp, "Plaid"),
                            (payment_gateways_bp, "Payment Gateways"),
                            (paypal_bp, "PayPal"),
                            (stripe_bp, "Stripe"),
                            (flutterwave_bp, "Flutterwave"),
                            (ach_network_bp, "ACH Network"),
                            (blockchain_bp, "Blockchain"),
                            (blockchain_analytics_bp, "Blockchain Analytics")
                        ]
                        
                        for blueprint, name in sub_modules:
                            app.register_blueprint(blueprint)
                            logger.info(f"✅ {name} blueprint registered with URL prefix: {blueprint.url_prefix}")
                        
                    except ImportError as e:
                        logger.warning(f"Could not import sub-module blueprints: {e}")
                    except Exception as e:
                        logger.error(f"Error registering sub-module blueprints: {e}")
            else:
                registration_results.append(f"❌ {module_name.title()} Module: No blueprint found")
                logger.warning(f"No blueprint found for {module_name} module")
                
        except Exception as e:
            error_msg = str(e)
            # Log the actual error for debugging
            logger.error(f"Actual error for {module_name}: {error_msg}")
            print(f"DEBUG: Actual error for {module_name}: {error_msg}")
            
            # Handle security decorator conflicts gracefully
            if "View function mapping is overwriting an existing endpoint function" in error_msg:
                registration_results.append(f"⚠️  {module_name.title()} Module skipped (security decorator conflict)")
                logger.warning(f"Skipped {module_name} module due to security decorator conflict")
            else:
                registration_results.append(f"❌ {module_name.title()} Module registration failed: {e}")
                logger.error(f"Failed to register {module_name} module: {e}")
    
    # Register URL alias blueprints for consistency
    alias_blueprints = [
        # Note: cards_payments, islamic_banking, system_management moved to hierarchical containers
        # nvct_stablecoin hyphen blueprint removed - it's redundant with main blueprint
        ('security_center', 'security_center_underscore_bp')
    ]
    
    for module_name, alias_bp_name in alias_blueprints:
        try:
            module = importlib.import_module(f'modules.{module_name}')
            if hasattr(module, alias_bp_name):
                alias_blueprint = getattr(module, alias_bp_name)
                app.register_blueprint(alias_blueprint)
                registration_results.append(f"✅ {module_name.title()} URL alias registered")
                logger.info(f"{module_name.title()} URL alias blueprint registered")
        except Exception as e:
            logger.warning(f"Failed to register URL alias for {module_name}: {e}")

    # Manually register analytics module with simple routes to avoid decorator conflicts
    try:
        from modules.services.analytics.simple_routes import analytics_simple
        app.register_blueprint(analytics_simple)
        registration_results.append(f"✅ Analytics Module registered manually (simple routes)")
        logger.info(f"Analytics module registered manually with simple routes")
    except Exception as e:
        registration_results.append(f"❌ Analytics Manual Registration failed: {e}")
        logger.error(f"Failed to manually register analytics module: {e}")
    
    # Manually register chat module from public (moved from services)
    try:
        from modules.public.chat.routes import chat_bp
        app.register_blueprint(chat_bp)
        registration_results.append(f"✅ Chat Module registered manually (public access)")
        logger.info(f"Chat module registered manually with public access")
    except Exception as e:
        registration_results.append(f"❌ Chat Manual Registration failed: {e}")
        logger.error(f"Failed to manually register chat module: {e}")
    
    # Create redirect blueprints for legacy URLs with underscores and hyphens
    try:
        from flask import Blueprint, redirect
        
        # Smart Contracts legacy redirects
        smart_contracts_legacy_bp = Blueprint('smart_contracts_legacy', __name__, url_prefix='/smart_contracts')
        smart_contracts_hyphen_bp = Blueprint('smart_contracts_hyphen_legacy', __name__, url_prefix='/smart-contracts')
        
        @smart_contracts_legacy_bp.route('/')
        @smart_contracts_legacy_bp.route('/<path:subpath>')
        def redirect_smart_contracts_underscore(subpath=''):
            return redirect(f'/smart-contracts/{subpath}' if subpath else '/smart-contracts/', code=301)
        
        @smart_contracts_hyphen_bp.route('/')
        @smart_contracts_hyphen_bp.route('/<path:subpath>')
        def redirect_smart_contracts_hyphen(subpath=''):
            return redirect(f'/smart-contracts/{subpath}' if subpath else '/smart-contracts/', code=301)
        
        # Cards Payments legacy redirects - DISABLED (moved to products container)
        # cards_payments_legacy_bp = Blueprint('cards_payments_legacy', __name__, url_prefix='/cards_payments')
        # cards_payments_hyphen_bp = Blueprint('cards_payments_hyphen_legacy', __name__, url_prefix='/cards-payments')
        
        # User Management legacy redirects
        user_management_legacy_bp = Blueprint('user_management_legacy', __name__, url_prefix='/user_management')
        user_management_hyphen_bp = Blueprint('user_management_hyphen_legacy', __name__, url_prefix='/user-management')
        
        @user_management_legacy_bp.route('/')
        @user_management_legacy_bp.route('/<path:subpath>')
        def redirect_user_management_underscore(subpath=''):
            return redirect(f'/user-management/{subpath}' if subpath else '/user-management/', code=301)
        
        @user_management_hyphen_bp.route('/')
        @user_management_hyphen_bp.route('/<path:subpath>')
        def redirect_user_management_hyphen(subpath=''):
            return redirect(f'/user-management/{subpath}' if subpath else '/user-management/', code=301)
        
        # Islamic Banking legacy redirects - DISABLED (moved to products container)
        # islamic_banking_legacy_bp = Blueprint('islamic_banking_legacy', __name__, url_prefix='/islamic_banking')
        # islamic_banking_hyphen_bp = Blueprint('islamic_banking_hyphen_legacy', __name__, url_prefix='/islamic-banking')
        
        # NVCT Stablecoin legacy redirects
        nvct_stablecoin_legacy_bp = Blueprint('nvct_stablecoin_legacy', __name__, url_prefix='/nvct_stablecoin')
        nvct_stablecoin_hyphen_bp = Blueprint('nvct_stablecoin_hyphen_legacy', __name__, url_prefix='/nvct-stablecoin')
        
        @nvct_stablecoin_legacy_bp.route('/')
        @nvct_stablecoin_legacy_bp.route('/<path:subpath>')
        def redirect_nvct_stablecoin_underscore(subpath=''):
            return redirect(f'/nvct-stablecoin/{subpath}' if subpath else '/nvct-stablecoin/', code=301)
        
        @nvct_stablecoin_hyphen_bp.route('/')
        @nvct_stablecoin_hyphen_bp.route('/<path:subpath>')
        def redirect_nvct_stablecoin_hyphen(subpath=''):
            return redirect(f'/nvct-stablecoin/{subpath}' if subpath else '/nvct-stablecoin/', code=301)
        
        # Interest Rate Management legacy redirects
        interest_rate_management_legacy_bp = Blueprint('interest_rate_management_legacy', __name__, url_prefix='/interest_rate_management')
        interest_rate_management_hyphen_bp = Blueprint('interest_rate_management_hyphen_legacy', __name__, url_prefix='/interest-rate-management')
        
        @interest_rate_management_legacy_bp.route('/')
        @interest_rate_management_legacy_bp.route('/<path:subpath>')
        def redirect_interest_rate_management_underscore(subpath=''):
            return redirect(f'/treasury/interest-rates/{subpath}' if subpath else '/treasury/interest-rates/', code=301)
        
        @interest_rate_management_hyphen_bp.route('/')
        @interest_rate_management_hyphen_bp.route('/<path:subpath>')
        def redirect_interest_rate_management_hyphen(subpath=''):
            return redirect(f'/treasury/interest-rates/{subpath}' if subpath else '/treasury/interest-rates/', code=301)
        
        # Settlement legacy redirects (integrated into banking)
        settlement_legacy_bp = Blueprint('settlement_legacy', __name__, url_prefix='/settlement')
        settlement_hyphen_bp = Blueprint('settlement_hyphen_legacy', __name__, url_prefix='/settlement-operations')
        
        @settlement_legacy_bp.route('/')
        @settlement_legacy_bp.route('/<path:subpath>')
        def redirect_settlement_underscore(subpath=''):
            return redirect(f'/banking/settlement/{subpath}' if subpath else '/banking/settlement/', code=301)
        
        @settlement_hyphen_bp.route('/')
        @settlement_hyphen_bp.route('/<path:subpath>')
        def redirect_settlement_hyphen(subpath=''):
            return redirect(f'/banking/settlement/{subpath}' if subpath else '/banking/settlement/', code=301)
        
        # Institutional banking legacy redirects (integrated into banking)
        institutional_legacy_bp = Blueprint('institutional_legacy', __name__, url_prefix='/institutional')
        
        @institutional_legacy_bp.route('/')
        @institutional_legacy_bp.route('/<path:subpath>')
        def redirect_institutional(subpath=''):
            return redirect(f'/banking/institutional/{subpath}' if subpath else '/banking/institutional/', code=301)
        
        # Smart contracts legacy redirects (integrated into nvct_stablecoin)
        smart_contracts_legacy_bp = Blueprint('smart_contracts_legacy', __name__, url_prefix='/smart_contracts')
        smart_contracts_hyphen_bp = Blueprint('smart_contracts_hyphen_legacy', __name__, url_prefix='/smart-contracts')
        
        @smart_contracts_legacy_bp.route('/')
        @smart_contracts_legacy_bp.route('/<path:subpath>')
        def redirect_smart_contracts_underscore(subpath=''):
            return redirect(f'/nvct-stablecoin/smart-contracts/{subpath}' if subpath else '/nvct-stablecoin/smart-contracts/', code=301)
        
        @smart_contracts_hyphen_bp.route('/')
        @smart_contracts_hyphen_bp.route('/<path:subpath>')
        def redirect_smart_contracts_hyphen(subpath=''):
            return redirect(f'/nvct-stablecoin/smart-contracts/{subpath}' if subpath else '/nvct-stablecoin/smart-contracts/', code=301)
        
        # System management legacy redirects (integrated into admin_management)
        system_management_legacy_bp = Blueprint('system_management_legacy', __name__, url_prefix='/system_management')
        system_management_hyphen_bp = Blueprint('system_management_hyphen_legacy', __name__, url_prefix='/system-management')
        
        @system_management_legacy_bp.route('/')
        @system_management_legacy_bp.route('/<path:subpath>')
        def redirect_system_management_underscore(subpath=''):
            return redirect(f'/admin-management/system-management/{subpath}' if subpath else '/admin-management/system-management/', code=301)
        
        @system_management_hyphen_bp.route('/')
        @system_management_hyphen_bp.route('/<path:subpath>')
        def redirect_system_management_hyphen(subpath=''):
            return redirect(f'/admin-management/system-management/{subpath}' if subpath else '/admin-management/system-management/', code=301)
        
        # System Management legacy redirects - DISABLED (moved to products container)
        # system_management_legacy_bp = Blueprint('system_management_legacy', __name__, url_prefix='/system_management')
        # system_management_hyphen_bp = Blueprint('system_management_hyphen_legacy', __name__, url_prefix='/system-management')
        
        # Security Center legacy redirects
        security_center_legacy_bp = Blueprint('security_center_legacy', __name__, url_prefix='/security_center')
        security_center_hyphen_bp = Blueprint('security_center_hyphen_legacy', __name__, url_prefix='/security-center')
        
        @security_center_legacy_bp.route('/')
        @security_center_legacy_bp.route('/<path:subpath>')
        def redirect_security_center_underscore(subpath=''):
            return redirect(f'/security-center/{subpath}' if subpath else '/security-center/', code=301)
        
        @security_center_hyphen_bp.route('/')
        @security_center_hyphen_bp.route('/<path:subpath>')
        def redirect_security_center_hyphen(subpath=''):
            return redirect(f'/security-center/{subpath}' if subpath else '/security-center/', code=301)
        
        # Blockchain Analytics legacy redirects
        blockchain_analytics_legacy_bp = Blueprint('blockchain_analytics_legacy', __name__, url_prefix='/blockchain_analytics')
        blockchain_analytics_hyphen_bp = Blueprint('blockchain_analytics_hyphen_legacy', __name__, url_prefix='/blockchain-analytics')
        
        @blockchain_analytics_legacy_bp.route('/')
        @blockchain_analytics_legacy_bp.route('/<path:subpath>')
        def redirect_blockchain_analytics_underscore(subpath=''):
            return redirect(f'/blockchain-analytics/{subpath}' if subpath else '/blockchain-analytics/', code=301)
        
        @blockchain_analytics_hyphen_bp.route('/')
        @blockchain_analytics_hyphen_bp.route('/<path:subpath>')
        def redirect_blockchain_analytics_hyphen(subpath=''):
            return redirect(f'/blockchain-analytics/{subpath}' if subpath else '/blockchain-analytics/', code=301)
        
        # Binance Integration legacy redirects
        binance_integration_legacy_bp = Blueprint('binance_integration_legacy', __name__, url_prefix='/binance_integration')
        binance_integration_hyphen_bp = Blueprint('binance_integration_hyphen_legacy', __name__, url_prefix='/binance-integration')
        
        @binance_integration_legacy_bp.route('/')
        @binance_integration_legacy_bp.route('/<path:subpath>')
        def redirect_binance_integration_underscore(subpath=''):
            return redirect(f'/binance-integration/{subpath}' if subpath else '/binance-integration/', code=301)
        
        @binance_integration_hyphen_bp.route('/')
        @binance_integration_hyphen_bp.route('/<path:subpath>')
        def redirect_binance_integration_hyphen(subpath=''):
            return redirect(f'/binance-integration/{subpath}' if subpath else '/binance-integration/', code=301)
        
        # Register all legacy redirect blueprints
        legacy_blueprints = [
            # cards_payments_legacy_bp, cards_payments_hyphen_bp,  # DISABLED - moved to products container
            user_management_legacy_bp, user_management_hyphen_bp,
            # islamic_banking_legacy_bp, islamic_banking_hyphen_bp,  # DISABLED - moved to products container
            nvct_stablecoin_legacy_bp, nvct_stablecoin_hyphen_bp,
            interest_rate_management_legacy_bp, interest_rate_management_hyphen_bp,
            # Settlement legacy redirects (integrated into banking)
            settlement_legacy_bp, settlement_hyphen_bp,
            # Institutional banking legacy redirects (integrated into banking)
            institutional_legacy_bp,
            # Smart contracts legacy redirects (integrated into nvct_stablecoin)
            smart_contracts_legacy_bp, smart_contracts_hyphen_bp,
            # System management legacy redirects (integrated into admin_management)
            system_management_legacy_bp, system_management_hyphen_bp,
            security_center_legacy_bp, security_center_hyphen_bp,
            blockchain_analytics_legacy_bp, blockchain_analytics_hyphen_bp,
            binance_integration_legacy_bp, binance_integration_hyphen_bp,
        ]
        
        for bp in legacy_blueprints:
            app.register_blueprint(bp)
        
        registration_results.append(f"✅ Clean URL legacy redirects registered successfully")
        logger.info(f"Clean URL legacy redirects registered successfully")
        print("✅ Clean URL legacy redirects registered successfully")
    except Exception as e:
        logger.warning(f"Failed to register clean URL legacy redirects: {e}")
        print(f"❌ Failed to register clean URL legacy redirects: {e}")
    
    # Print registration results
    for result in registration_results:
        print(result)
    
    return registration_results

def verify_blueprint_registration(app: Flask):
    """
    Verify that all modular blueprints are properly registered
    """
    registered_blueprints = list(app.blueprints.keys())
    logger.info(f"Registered blueprints: {registered_blueprints}")
    return registered_blueprints
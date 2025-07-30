"""
Enterprise Secrets Management for NVC Banking Platform
AWS Secrets Manager with HashiCorp Vault fallback implementation

SECURITY NOTE: This module handles sensitive credentials.
- All logging masks sensitive information
- Credentials are never exposed in logs or error messages
- Use appropriate log levels in production
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from functools import lru_cache

logger = logging.getLogger(__name__)

class SecretsManager:
    """
    Enterprise secrets management with AWS Secrets Manager primary and HashiCorp Vault fallback
    """
    
    def __init__(self):
        self.aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        self.vault_url = os.environ.get('VAULT_URL', 'http://localhost:8200')
        self.vault_token = os.environ.get('VAULT_TOKEN')
        self._aws_client = None
        self._vault_client = None
        
    @property
    def aws_client(self):
        """Lazy initialization of AWS Secrets Manager client"""
        if self._aws_client is None:
            try:
                import boto3
                from botocore.exceptions import NoCredentialsError, ClientError
                
                self._aws_client = boto3.client(
                    'secretsmanager',
                    region_name=self.aws_region
                )
                
                # Test AWS credentials
                self._aws_client.list_secrets(MaxResults=1)
                logger.info("AWS Secrets Manager client initialized successfully")
                
            except (ImportError, NoCredentialsError, ClientError) as e:
                logger.warning(f"AWS Secrets Manager not available: {e}")
                self._aws_client = False  # Mark as unavailable
                
        return self._aws_client if self._aws_client is not False else None
    
    @property
    def vault_client(self):
        """Lazy initialization of HashiCorp Vault client"""
        if self._vault_client is None:
            try:
                import hvac
                
                self._vault_client = hvac.Client(
                    url=self.vault_url,
                    token=self.vault_token
                )
                
                # Test Vault connection
                if self._vault_client.is_authenticated():
                    logger.info("HashiCorp Vault client initialized successfully")
                else:
                    logger.warning("Vault client not authenticated")
                    self._vault_client = False
                    
            except (ImportError, Exception) as e:
                logger.warning(f"HashiCorp Vault not available: {e}")
                self._vault_client = False
                
        return self._vault_client if self._vault_client is not False else None
    
    def get_secret_from_aws(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve secret from AWS Secrets Manager"""
        if not self.aws_client:
            return None
            
        try:
            response = self.aws_client.get_secret_value(SecretId=secret_name)
            secret_string = response.get('SecretString')
            
            if secret_string:
                try:
                    return json.loads(secret_string)
                except json.JSONDecodeError:
                    # Return as string if not JSON
                    return {'value': secret_string}
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}' from AWS: {e}")
            return None
    
    def get_secret_from_vault(self, secret_path: str, mount_point: str = 'secret') -> Optional[Dict[str, Any]]:
        """Retrieve secret from HashiCorp Vault with multiple mount points and versions"""
        if not self.vault_client:
            return None

        # Try different mount points
        mount_points = [mount_point, 'kv-v2', 'kv', 'secrets', 'app']

        for mp in mount_points:
            try:
                # Try KV v2 first (default for newer Vault installations)
                try:
                    response = self.vault_client.secrets.kv.v2.read_secret_version(
                        path=secret_path,
                        mount_point=mp
                    )
                    return response['data']['data']
                except Exception as v2_error:
                    # Try KV v1
                    try:
                        response = self.vault_client.secrets.kv.v1.read_secret(
                            path=secret_path,
                            mount_point=mp
                        )
                        return response['data']
                    except Exception as v1_error:
                        # Try direct read (for custom engines)
                        try:
                            response = self.vault_client.read(f"{mp}/{secret_path}")
                            if response and 'data' in response:
                                return response['data']
                        except Exception:
                            continue

            except Exception as e:
                # Only log debug for connection errors, not missing secrets
                if "connection" in str(e).lower() or "refused" in str(e).lower():
                    logger.debug(f"Vault connection issue for mount '{mp}': {e}")
                continue

        logger.debug(f"Failed to retrieve secret '{secret_path}' from any Vault mount point")
        return None
    
    @lru_cache(maxsize=32)
    def get_secret(self, secret_name: str, vault_path: str = None) -> Optional[Union[str, Dict[str, Any]]]:
        """
        Get secret with AWS Secrets Manager primary, Vault fallback
        
        Args:
            secret_name: AWS secret name or environment variable name
            vault_path: Vault secret path (if different from secret_name)
            
        Returns:
            Secret value or None if not found
        """
        vault_path = vault_path or secret_name
        
        # Try AWS Secrets Manager first
        aws_secret = self.get_secret_from_aws(secret_name)
        if aws_secret:
            logger.debug(f"Retrieved secret '{secret_name}' from AWS Secrets Manager")
            return aws_secret
        
        # Fallback to HashiCorp Vault
        vault_secret = self.get_secret_from_vault(vault_path)
        if vault_secret:
            logger.debug(f"Retrieved secret '{vault_path}' from HashiCorp Vault")
            return vault_secret
        
        # Final fallback to environment variable
        env_value = os.environ.get(secret_name)
        if env_value:
            logger.debug(f"Retrieved secret '{secret_name}' from environment variable")
            return env_value
        
        logger.warning(f"Secret '{secret_name}' not found in AWS, Vault, or environment")
        return None
    
    def get_database_url(self) -> Optional[str]:
        """Get database URL with proper fallback chain"""
        # Try multiple AWS secret names
        for secret_name in ['nvc-banking/database', 'nvcfund/database', 'database']:
            db_secret = self.get_secret_from_aws(secret_name)
            if db_secret and isinstance(db_secret, dict):
                # Try direct DATABASE_URL first
                db_url = db_secret.get('DATABASE_URL') or db_secret.get('database_url')
                if db_url:
                    return db_url

                # Try constructing from components
                db_url = self._construct_database_url(db_secret)
                if db_url:
                    return db_url

        # Try multiple Vault paths
        for path in ['nvc-banking/database', 'nvcfund/database', 'database', 'app/database']:
            vault_secret = self.get_secret_from_vault(path)
            if vault_secret:
                # Try direct DATABASE_URL first
                db_url = vault_secret.get('DATABASE_URL') or vault_secret.get('database_url')
                if db_url:
                    return db_url

                # Try constructing from components
                db_url = self._construct_database_url(vault_secret)
                if db_url:
                    return db_url

        # Environment variable fallback
        return os.environ.get('DATABASE_URL')

    def _construct_database_url(self, secret_data: Dict[str, Any]) -> Optional[str]:
        """Construct DATABASE_URL from individual components"""
        try:
            username = secret_data.get('username') or secret_data.get('user')
            password = secret_data.get('password') or secret_data.get('pass')
            host = secret_data.get('host') or secret_data.get('hostname')
            port = secret_data.get('port')
            database = secret_data.get('database') or secret_data.get('db') or secret_data.get('dbname')

            if username and host and database:
                # Construct PostgreSQL URL
                url = f"postgresql://{username}"
                if password:
                    url += f":{password}"
                url += f"@{host}"
                if port:
                    url += f":{port}"
                url += f"/{database}"

                logger.info(f"Constructed database URL from components: postgresql://***@{host}:{port}/{database}")
                return url

        except Exception as e:
            logger.error(f"Failed to construct database URL from components: {e}")

        return None
    
    def get_session_secret(self) -> Optional[str]:
        """Get session secret with proper fallback chain"""
        # Try multiple AWS secret names
        for secret_name in ['nvc-banking/session', 'nvcfund/session', 'session', 'app/session']:
            session_secret = self.get_secret_from_aws(secret_name)
            if session_secret and isinstance(session_secret, dict):
                secret = session_secret.get('SESSION_SECRET') or session_secret.get('session_secret')
                if secret:
                    return secret

        # Try multiple Vault paths
        for path in ['nvc-banking/session', 'nvcfund/session', 'session', 'app/session']:
            vault_secret = self.get_secret_from_vault(path)
            if vault_secret:
                secret = vault_secret.get('SESSION_SECRET') or vault_secret.get('session_secret')
                if secret:
                    return secret

        # Environment variable fallback
        env_secret = os.environ.get('SESSION_SECRET')
        if env_secret:
            return env_secret

        # Development fallback - generate a secure random secret
        import secrets
        dev_secret = secrets.token_urlsafe(32)
        logger.warning("Using generated session secret for development. Set SESSION_SECRET environment variable for production.")
        return dev_secret
    
    def get_application_secrets(self) -> Dict[str, Any]:
        """Get all application secrets"""
        secrets = {}
        
        # Try AWS Secrets Manager
        aws_secrets = self.get_secret('nvc-banking/application')
        if aws_secrets and isinstance(aws_secrets, dict):
            secrets.update(aws_secrets)
        
        # Try Vault for missing secrets
        vault_secrets = self.get_secret_from_vault('nvc-banking/application')
        if vault_secrets:
            for key, value in vault_secrets.items():
                if key not in secrets:
                    secrets[key] = value
        
        # Environment variable fallbacks
        env_secrets = {
            'MAIL_USERNAME': os.environ.get('MAIL_USERNAME'),
            'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD'),
            'PLAID_CLIENT_ID': os.environ.get('PLAID_CLIENT_ID'),
            'PLAID_SECRET': os.environ.get('PLAID_SECRET'),
            'DATA_ENCRYPTION_KEY': os.environ.get('DATA_ENCRYPTION_KEY'),
            'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY')
        }
        
        for key, value in env_secrets.items():
            if key not in secrets and value:
                secrets[key] = value
        
        return secrets


# Global secrets manager instance
secrets_manager = SecretsManager()

# Convenience functions
def get_secret(secret_name: str, vault_path: str = None) -> Optional[Union[str, Dict[str, Any]]]:
    """Get secret using the global secrets manager"""
    return secrets_manager.get_secret(secret_name, vault_path)

def get_database_url() -> Optional[str]:
    """Get database URL using the global secrets manager"""
    return secrets_manager.get_database_url()

def get_session_secret() -> Optional[str]:
    """Get session secret using the global secrets manager"""
    return secrets_manager.get_session_secret()

def get_application_secrets() -> Dict[str, Any]:
    """Get application secrets using the global secrets manager"""
    return secrets_manager.get_application_secrets()

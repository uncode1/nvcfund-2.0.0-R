"""
Database Migration System
Automatic schema migration for NVC Banking Platform
"""

import logging
from sqlalchemy import text, inspect
from typing import Dict, List, Any
from modules.core.extensions import db

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """
    Automatic database migration system for handling schema changes
    """
    
    def __init__(self):
        self.migrations_applied = []
        
    def check_and_apply_migrations(self):
        """
        Check for missing columns and apply necessary migrations
        """
        try:
            with db.engine.connect() as connection:
                # Check and apply User table migrations
                self._migrate_users_table(connection)
                
                # Check and apply KYC verifications table migrations
                self._migrate_kyc_verifications_table(connection)
                
                # Check and apply other table migrations
                self._migrate_communications_tables(connection)
                self._migrate_security_events_table(connection)
                self._migrate_logs_tables(connection)
                
                logger.info(f"Database migrations completed. Applied: {len(self.migrations_applied)}")
                return True
                
        except Exception as e:
            logger.error(f"Database migration error: {e}")
            return False
    
    def _column_exists(self, connection, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table"""
        try:
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name AND column_name = :column_name
            """), {"table_name": table_name, "column_name": column_name})
            return result.fetchone() is not None
        except Exception:
            return False
    
    def _migrate_users_table(self, connection):
        """Apply migrations for users table"""
        migrations = [
            {
                'column': 'kyc_status',
                'sql': "ALTER TABLE users ADD COLUMN kyc_status VARCHAR(20) DEFAULT 'pending'",
                'description': 'Add KYC status tracking'
            },
            {
                'column': 'last_activity',
                'sql': "ALTER TABLE users ADD COLUMN last_activity TIMESTAMP",
                'description': 'Add last activity tracking'
            }
        ]
        
        for migration in migrations:
            if not self._column_exists(connection, 'users', migration['column']):
                try:
                    connection.execute(text(migration['sql']))
                    connection.commit()
                    self.migrations_applied.append(f"users.{migration['column']}")
                    logger.info(f"Applied migration: {migration['description']}")
                except Exception as e:
                    logger.warning(f"Migration failed for users.{migration['column']}: {e}")
    
    def _migrate_kyc_verifications_table(self, connection):
        """Apply migrations for kyc_verifications table"""
        # First check if table exists
        table_exists = connection.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'kyc_verifications'
        """)).fetchone()
        
        if not table_exists:
            logger.info("KYC verifications table doesn't exist yet - will be created by create_all()")
            return
            
        migrations = [
            {
                'column': 'verification_level',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN verification_level VARCHAR(20) DEFAULT 'basic'",
                'description': 'Add verification level tracking'
            },
            {
                'column': 'identity_document_type',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN identity_document_type VARCHAR(50)",
                'description': 'Add identity document type field'
            },
            {
                'column': 'identity_document_number',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN identity_document_number VARCHAR(100)",
                'description': 'Add identity document number field'
            },
            {
                'column': 'identity_document_expiry',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN identity_document_expiry TIMESTAMP",
                'description': 'Add identity document expiry date'
            },
            {
                'column': 'identity_verified',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN identity_verified BOOLEAN DEFAULT FALSE",
                'description': 'Add identity verification status'
            },
            {
                'column': 'proof_of_address_type',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN proof_of_address_type VARCHAR(50)",
                'description': 'Add proof of address type field'
            },
            {
                'column': 'address_verified',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN address_verified BOOLEAN DEFAULT FALSE",
                'description': 'Add address verification status'
            },
            {
                'column': 'business_registration_number',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN business_registration_number VARCHAR(100)",
                'description': 'Add business registration number'
            },
            {
                'column': 'tax_identification_number',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN tax_identification_number VARCHAR(50)",
                'description': 'Add tax identification number'
            },
            {
                'column': 'business_license_number',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN business_license_number VARCHAR(100)",
                'description': 'Add business license number'
            },
            {
                'column': 'business_verified',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN business_verified BOOLEAN DEFAULT FALSE",
                'description': 'Add business verification status'
            },
            {
                'column': 'income_verification_type',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN income_verification_type VARCHAR(50)",
                'description': 'Add income verification type'
            },
            {
                'column': 'income_amount',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN income_amount NUMERIC(18, 2)",
                'description': 'Add income amount field'
            },
            {
                'column': 'source_of_funds',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN source_of_funds VARCHAR(200)",
                'description': 'Add source of funds field'
            },
            {
                'column': 'financial_verified',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN financial_verified BOOLEAN DEFAULT FALSE",
                'description': 'Add financial verification status'
            },
            {
                'column': 'risk_score',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN risk_score INTEGER",
                'description': 'Add risk score field'
            },
            {
                'column': 'risk_category',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN risk_category VARCHAR(20)",
                'description': 'Add risk category field'
            },
            {
                'column': 'sanctions_check_passed',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN sanctions_check_passed BOOLEAN DEFAULT FALSE",
                'description': 'Add sanctions check status'
            },
            {
                'column': 'pep_check_passed',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN pep_check_passed BOOLEAN DEFAULT FALSE",
                'description': 'Add PEP check status'
            },
            {
                'column': 'verified_by',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN verified_by VARCHAR(36)",
                'description': 'Add verified by user ID'
            },
            {
                'column': 'verification_notes',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN verification_notes TEXT",
                'description': 'Add verification notes field'
            },
            {
                'column': 'compliance_officer_notes',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN compliance_officer_notes TEXT",
                'description': 'Add compliance officer notes'
            },
            {
                'column': 'documents_uploaded',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN documents_uploaded BOOLEAN DEFAULT FALSE",
                'description': 'Add documents uploaded status'
            },
            {
                'column': 'documents_verified',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN documents_verified BOOLEAN DEFAULT FALSE",
                'description': 'Add documents verified status'
            },
            {
                'column': 'verification_date',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN verification_date TIMESTAMP",
                'description': 'Add verification date'
            },
            {
                'column': 'expiry_date',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN expiry_date TIMESTAMP",
                'description': 'Add verification expiry date'
            },
            {
                'column': 'next_review_date',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN next_review_date TIMESTAMP",
                'description': 'Add next review date'
            },
            {
                'column': 'created_at',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                'description': 'Add created timestamp'
            },
            {
                'column': 'updated_at',
                'sql': "ALTER TABLE kyc_verifications ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                'description': 'Add updated timestamp'
            }
        ]
        
        for migration in migrations:
            if not self._column_exists(connection, 'kyc_verifications', migration['column']):
                try:
                    connection.execute(text(migration['sql']))
                    connection.commit()
                    self.migrations_applied.append(f"kyc_verifications.{migration['column']}")
                    logger.info(f"Applied migration: {migration['description']}")
                except Exception as e:
                    logger.warning(f"Migration failed for kyc_verifications.{migration['column']}: {e}")
    
    def _migrate_communications_tables(self, connection):
        """Apply migrations for communications-related tables"""
        # Check if communications tables exist and need updates
        tables_to_check = ['communication_logs', 'communication_preferences']
        
        for table_name in tables_to_check:
            table_exists = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = :table_name
            """), {"table_name": table_name}).fetchone()
            
            if not table_exists:
                logger.info(f"{table_name} table doesn't exist yet - will be created by create_all()")
                continue
                
            # Add any future migrations for communications tables here
            # Example:
            # if not self._column_exists(connection, table_name, 'new_column'):
            #     # Apply migration
    
    def _migrate_security_events_table(self, connection):
        """Apply migrations for security_events table"""
        migrations = [
            {
                'column': 'category',
                'sql': "ALTER TABLE security_events ADD COLUMN category VARCHAR(50) DEFAULT 'system'",
                'description': 'Add security event category'
            },
            {
                'column': 'title',
                'sql': "ALTER TABLE security_events ADD COLUMN title VARCHAR(200) DEFAULT 'Security Event'",
                'description': 'Add security event title'
            },
            {
                'column': 'source',
                'sql': "ALTER TABLE security_events ADD COLUMN source VARCHAR(100)",
                'description': 'Add security event source'
            },
            {
                'column': 'source_ip',
                'sql': "ALTER TABLE security_events ADD COLUMN source_ip VARCHAR(45)",
                'description': 'Add security event source IP'
            },
            {
                'column': 'target_system',
                'sql': "ALTER TABLE security_events ADD COLUMN target_system VARCHAR(100)",
                'description': 'Add security event target system'
            },
            {
                'column': 'user_agent',
                'sql': "ALTER TABLE security_events ADD COLUMN user_agent TEXT",
                'description': 'Add security event user agent'
            },
            {
                'column': 'event_data',
                'sql': "ALTER TABLE security_events ADD COLUMN event_data JSONB",
                'description': 'Add security event data'
            },
            {
                'column': 'indicators',
                'sql': "ALTER TABLE security_events ADD COLUMN indicators TEXT[]",
                'description': 'Add security event indicators'
            },
            {
                'column': 'status',
                'sql': "ALTER TABLE security_events ADD COLUMN status VARCHAR(20) DEFAULT 'open'",
                'description': 'Add security event status'
            },
            {
                'column': 'assigned_to',
                'sql': "ALTER TABLE security_events ADD COLUMN assigned_to VARCHAR(100)",
                'description': 'Add security event assigned to'
            },
            {
                'column': 'resolution_notes',
                'sql': "ALTER TABLE security_events ADD COLUMN resolution_notes TEXT",
                'description': 'Add security event resolution notes'
            },
            {
                'column': 'created_at',
                'sql': "ALTER TABLE security_events ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                'description': 'Add security event created timestamp'
            },
            {
                'column': 'updated_at',
                'sql': "ALTER TABLE security_events ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                'description': 'Add security event updated timestamp'
            },
            {
                'column': 'resolved_at',
                'sql': "ALTER TABLE security_events ADD COLUMN resolved_at TIMESTAMP",
                'description': 'Add security event resolved timestamp'
            },
            {
                'column': 'event_timestamp',
                'sql': "ALTER TABLE security_events ADD COLUMN event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                'description': 'Add security event timestamp'
            }
        ]
        
        # Handle column renaming for timestamp -> event_timestamp
        try:
            # Check if old 'timestamp' column exists and new 'event_timestamp' doesn't
            has_timestamp = self._column_exists(connection, 'security_events', 'timestamp')
            has_event_timestamp = self._column_exists(connection, 'security_events', 'event_timestamp')
            
            if has_timestamp and not has_event_timestamp:
                connection.execute(text("ALTER TABLE security_events RENAME COLUMN timestamp TO event_timestamp"))
                connection.commit()
                self.migrations_applied.append("security_events.timestamp_rename")
                logger.info("Renamed timestamp column to event_timestamp")
        except Exception as e:
            logger.warning(f"Failed to rename timestamp column: {e}")
        
        for migration in migrations:
            if not self._column_exists(connection, 'security_events', migration['column']):
                try:
                    connection.execute(text(migration['sql']))
                    connection.commit()
                    self.migrations_applied.append(f"security_events.{migration['column']}")
                    logger.info(f"Applied migration: {migration['description']}")
                except Exception as e:
                    logger.warning(f"Migration failed for security_events.{migration['column']}: {e}")
        
        logger.info("Security events table migration completed")
    
    def _migrate_logs_tables(self, connection):
        """Apply migrations for logging tables"""
        log_tables = [
            'system_logs', 'security_logs', 'transaction_logs', 
            'compliance_logs', 'api_logs'
        ]
        
        for table_name in log_tables:
            table_exists = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = :table_name
            """), {"table_name": table_name}).fetchone()
            
            if not table_exists:
                logger.info(f"{table_name} table doesn't exist yet - will be created by create_all()")
                continue
                
            # Add future column migrations here if needed
            logger.info(f"{table_name} table exists and is up to date")

    def get_migration_status(self) -> Dict[str, Any]:
        """Get status of all database migrations"""
        try:
            with db.engine.connect() as connection:
                status = {
                    'users_table': {
                        'kyc_status': self._column_exists(connection, 'users', 'kyc_status'),
                        'last_activity': self._column_exists(connection, 'users', 'last_activity')
                    },
                    'kyc_verifications_table': {
                        'verification_level': self._column_exists(connection, 'kyc_verifications', 'verification_level')
                    },
                    'last_applied': self.migrations_applied
                }
                return status
        except Exception as e:
            logger.error(f"Error getting migration status: {e}")
            return {'error': str(e)}

# Global migration instance
database_migration = DatabaseMigration()

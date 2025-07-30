#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script for NVC Banking Platform
Creates development and test databases
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

def create_database(db_name, user='postgres', password='password', host='localhost', port='5432'):
    """Create a PostgreSQL database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Created database: {db_name}")
        else:
            print(f"ℹ️  Database already exists: {db_name}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database {db_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def setup_databases():
    """Setup development and test databases"""
    print("🚀 Setting up PostgreSQL databases for NVC Banking Platform...")
    
    # Database configuration
    config = {
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'password'),
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': os.environ.get('POSTGRES_PORT', '5432')
    }
    
    databases = [
        'nvc_banking_dev',
        'nvc_banking_test'
    ]
    
    success_count = 0
    for db_name in databases:
        if create_database(db_name, **config):
            success_count += 1
    
    if success_count == len(databases):
        print(f"\n✅ All databases created successfully!")
        print(f"📝 Development database: postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/nvc_banking_dev")
        print(f"📝 Test database: postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/nvc_banking_test")
        print(f"\n🔧 To use these databases, set the following environment variables:")
        print(f"   export DATABASE_URL='postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/nvc_banking_dev'")
        print(f"   export TEST_DATABASE_URL='postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/nvc_banking_test'")
    else:
        print(f"\n❌ Failed to create {len(databases) - success_count} database(s)")
        sys.exit(1)

if __name__ == "__main__":
    setup_databases()

"""
Database Configuration for NVC Banking Platform
SQLAlchemy database instance and configuration
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session
from sqlalchemy import create_engine
import os

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

# Initialize SQLAlchemy with custom base class
db = SQLAlchemy(model_class=Base)

# Database session management
engine = None
SessionLocal = None

def init_database():
    """Initialize database engine and session factory"""
    global engine, SessionLocal
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        engine = create_engine(database_url)
        SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db_session():
    """Get database session"""
    if SessionLocal:
        return SessionLocal()
    else:
        # Fallback to Flask-SQLAlchemy session
        return db.session

def get_db_connection():
    """Get database connection"""
    if engine:
        return engine.connect()
    else:
        # Fallback to Flask-SQLAlchemy connection
        return db.engine.connect()

# Initialize on module import
init_database()
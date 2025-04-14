"""
Database Connection Module

This module manages database connections and sessions using SQLAlchemy.
It provides:
- A connection factory for creating database engines
- Connection pooling for performance optimization
- Session management with automatic cleanup
- Context manager for safe database operations

The module implements a connection pool to efficiently manage database
connections and provides a context manager to ensure proper session
handling and resource cleanup.

Usage:
    from app.database import get_db

    # Using the database session
    with get_db() as db:
        result = db.query(Model).all()
        # Session is automatically closed after the with block
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from app.config import DATABASE_CONFIG, DATABASE_URL
from contextlib import contextmanager
from typing import Generator

def get_database_engine():
    """
    Create and return a database engine with connection pooling.
    
    Returns:
        SQLAlchemy Engine: Configured database engine with connection pool
    
    Configuration:
        - pool_size: Maximum number of persistent connections
        - max_overflow: Maximum number of additional connections
        - pool_timeout: Seconds to wait for available connection
        - pool_recycle: Seconds before connection is recycled
    """
    return create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,  # Base number of persistent connections
        max_overflow=10,  # Allow up to 10 additional connections
        pool_timeout=30,  # Wait up to 30 seconds for available connection
        pool_recycle=1800  # Recycle connections after 30 minutes
    )

# Create the engine using the factory
engine = get_database_engine()

# Create session factory with transaction management
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Yields:
        Session: SQLAlchemy session for database operations
    
    Usage:
        with get_db() as db:
            db.query(Model).all()
    
    The session is automatically closed when exiting the with block,
    even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
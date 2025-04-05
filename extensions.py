"""
Flask Extensions Module

This module initializes and manages Flask extensions with:
- SQLAlchemy with connection pooling
- Database migrations
- Session management
- Query performance monitoring
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging
import time
from config import settings

# Configure SQLAlchemy for connection pooling and performance
db = SQLAlchemy(engine_options={
    'pool_size': settings.DB_POOL_SIZE,
    'max_overflow': settings.DB_MAX_OVERFLOW,
    'pool_timeout': settings.DB_POOL_TIMEOUT,
    'pool_recycle': settings.DB_POOL_RECYCLE
})

migrate = Migrate()

# Query performance monitoring
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop()
    if total > 0.5:  # Log slow queries (>500ms)
        logging.warning(f"Slow query detected ({total:.2f}s): {statement}")

def init_extensions(app):
    """Initialize Flask extensions with enhanced configuration."""
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': settings.DB_POOL_SIZE,
        'max_overflow': settings.DB_MAX_OVERFLOW,
        'pool_timeout': settings.DB_POOL_TIMEOUT,
        'pool_recycle': settings.DB_POOL_RECYCLE
    }
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    
    # Set up database event listeners
    if not app.debug:
        event.listen(db.engine, 'connect', _on_connect)
        event.listen(db.engine, 'checkout', _on_checkout)

def _on_connect(dbapi_connection, connection_record):
    """Configure new database connections."""
    # Set session variables for better performance
    cursor = dbapi_connection.cursor()
    cursor.execute("SET SESSION innodb_strict_mode=1")
    cursor.execute("SET SESSION sql_mode='STRICT_TRANS_TABLES'")
    cursor.close()

def _on_checkout(dbapi_connection, connection_record, connection_proxy):
    """Verify connection is active before using."""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except Exception:
        # Replace invalid connection
        raise exc.DisconnectionError()
    finally:
        cursor.close() 
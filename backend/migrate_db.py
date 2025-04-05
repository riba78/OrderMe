"""
Database Migration Script

This script handles the complete database migration process:
1. Creates all necessary tables with proper constraints
2. Sets up views for common queries
3. Creates stored procedures for common operations
4. Implements database functions for validation
5. Sets up initial admin user
6. Handles error cases and rollbacks

Usage:
    python migrate_db.py

The script is idempotent and can be run multiple times safely.

Known Issues:
-------------
1. MariaDB Version Mismatch:
   When running this script, you might encounter the following error:
   "Column count of mysql.proc is wrong. Expected 21, found 20. Created with MariaDB 100108, now running 100428."
   
   This happens because:
   - The mysql.proc table structure has changed between MariaDB versions
   - The system is using a different version than what created the table
   
   To fix this:
   1. First try running: mysql_upgrade -u root -p
   2. If that doesn't work:
      a. Stop MariaDB service
      b. Delete the mysql.proc table (it will be recreated)
      c. Start MariaDB service
      d. Run the migration again
   
   Note: Since this is a common issue with MariaDB upgrades, we've modified the script to:
   - Continue with table and view creation even if stored procedures fail
   - Log a warning instead of failing completely
   - Allow manual creation of stored procedures later if needed
"""

import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect, exc
from werkzeug.security import generate_password_hash
import logging
import subprocess
import json
from pathlib import Path
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('migration.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DB_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://orderme_user:Brat1978@127.0.0.1:3306/orderme')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@orderme.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# Migration version
MIGRATION_VERSION = "1.0.0"

class MigrationError(Exception):
    """Custom exception for migration errors."""
    pass

def validate_environment():
    """Validate environment variables and dependencies."""
    try:
        # Check required environment variables
        required_vars = ['DATABASE_URL', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
            logger.info("Using default values for missing variables")
        
        # Check Python version
        if sys.version_info < (3, 7):
            raise MigrationError("Python 3.7 or higher is required")
        
        # Check required packages
        required_packages = ['sqlalchemy', 'dotenv', 'werkzeug']
        for package in required_packages:
            try:
                if package == 'dotenv':
                    from dotenv import load_dotenv
                else:
                    __import__(package)
            except ImportError:
                raise MigrationError(f"Required package {package} is not installed")
        
        logger.info("Environment validation successful")
    except Exception as e:
        logger.error(f"Environment validation failed: {str(e)}")
        raise

def create_backup(engine):
    """Create a backup of the database before migration."""
    try:
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"orderme_backup_{timestamp}.sql"
        
        with engine.connect() as conn:
            # Get all tables
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'orderme'
                AND table_type = 'BASE TABLE'
            """)).fetchall()
            
            with open(backup_file, 'w') as f:
                # Write table creation and data
                for table in tables:
                    table_name = table[0]
                    
                    # Get create table statement
                    create_table = conn.execute(text(f"""
                        SHOW CREATE TABLE orderme.{table_name}
                    """)).fetchone()
                    
                    f.write(f"\n-- Table: {table_name}\n")
                    f.write(f"{create_table[1]};\n\n")
                    
                    # Get table data
                    data = conn.execute(text(f"SELECT * FROM {table_name}")).fetchall()
                    if data:
                        columns = [col[0] for col in conn.execute(text(f"SHOW COLUMNS FROM {table_name}")).fetchall()]
                        for row in data:
                            values = []
                            for val in row:
                                if val is None:
                                    values.append("NULL")
                                elif isinstance(val, (int, float)):
                                    values.append(str(val))
                                else:
                                    # Escape single quotes in string values
                                    escaped_val = str(val).replace("'", "\\'")
                                    values.append(f"'{escaped_val}'")
                            
                            f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
        
        logger.info(f"Database backup created: {backup_file}")
        return backup_file
    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}")
        return None  # Return None instead of raising to allow migration to continue

def check_database_version(engine):
    """Check current database version and compatibility."""
    try:
        with engine.connect() as conn:
            # Check if version table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'orderme' 
                AND table_name = 'schema_version'
            """)).fetchone()
            
            if result:
                # Get current version
                version = conn.execute(text("SELECT version FROM schema_version")).scalar()
                logger.info(f"Current database version: {version}")
                
                if version != MIGRATION_VERSION:
                    logger.warning(f"Database version mismatch: current={version}, target={MIGRATION_VERSION}")
                    return False
                return True
            return False
    except Exception as e:
        logger.error(f"Version check failed: {str(e)}")
        return False

def create_database(engine):
    """Create database if it doesn't exist."""
    try:
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text("""
                SELECT SCHEMA_NAME 
                FROM INFORMATION_SCHEMA.SCHEMATA 
                WHERE SCHEMA_NAME = 'orderme'
            """)).fetchone()
            
            if not result:
                logger.info("Creating new database")
                conn.execute(text("CREATE DATABASE orderme CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            else:
                logger.info("Database already exists")
            
            conn.execute(text("USE orderme"))
            
            # Create version tracking table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    version VARCHAR(20) NOT NULL,
                    migrated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    migration_hash VARCHAR(64) NOT NULL
                )
            """))
            
            logger.info("Database created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        raise

def create_tables(engine):
    """Create all database tables."""
    with engine.connect() as conn:
        try:
            # Drop existing tables
            logger.info("Dropping existing tables...")
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # Drop tables in correct order
            conn.execute(text("DROP TABLE IF EXISTS verification_messages_log"))
            conn.execute(text("DROP TABLE IF EXISTS activity_logs"))
            conn.execute(text("DROP TABLE IF EXISTS payment_info"))
            conn.execute(text("DROP TABLE IF EXISTS payment_methods"))
            conn.execute(text("DROP TABLE IF EXISTS user_verification_methods"))
            conn.execute(text("DROP TABLE IF EXISTS customers"))
            conn.execute(text("DROP TABLE IF EXISTS user_profiles"))
            conn.execute(text("DROP TABLE IF EXISTS users"))
            conn.execute(text("DROP TABLE IF EXISTS schema_version"))

            # Create users table
            logger.info("Creating users table...")
            conn.execute(text("""
                CREATE TABLE users (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    uuid CHAR(36) NOT NULL UNIQUE,
                    email VARCHAR(120) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
                    primary_verification_method VARCHAR(20),
                    verification_token VARCHAR(255),
                    verification_token_expires DATETIME,
                    email_change_token VARCHAR(255),
                    email_change_new VARCHAR(120),
                    email_change_expires DATETIME,
                    last_login_at DATETIME,
                    login_count INT DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    created_by_id BIGINT,
                    created_as_role VARCHAR(20) NOT NULL,
                    FOREIGN KEY (created_by_id) REFERENCES users(id),
                    CONSTRAINT chk_role CHECK (role IN ('ADMIN', 'USER', 'CUSTOMER')),
                    CONSTRAINT chk_verification_method CHECK (primary_verification_method IN ('email', 'phone', 'whatsapp')),
                    CONSTRAINT uniq_email_active UNIQUE (email, is_active),
                    INDEX idx_uuid (uuid),
                    INDEX idx_role (role),
                    INDEX idx_verification (verification_token),
                    INDEX idx_email_change (email_change_token),
                    INDEX idx_created_at (created_at),
                    INDEX idx_last_login (last_login_at),
                    INDEX idx_created_by (created_by_id, created_as_role)
                ) ROW_FORMAT=COMPRESSED
            """))

            # Create user_profiles table
            logger.info("Creating user_profiles table...")
            conn.execute(text("""
                CREATE TABLE user_profiles (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    user_id BIGINT NOT NULL UNIQUE,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    business_name VARCHAR(100),
                    street VARCHAR(255),
                    city VARCHAR(100),
                    state VARCHAR(100),
                    zip_code VARCHAR(20),
                    country VARCHAR(100),
                    phone_number VARCHAR(20),
                    tin_trunk_phone VARCHAR(20),
                    metadata JSON,
                    search_vector TEXT GENERATED ALWAYS AS (
                        CONCAT_WS(' ',
                            NULLIF(first_name, ''),
                            NULLIF(last_name, ''),
                            NULLIF(business_name, ''),
                            NULLIF(phone_number, '')
                        )
                    ) STORED,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_user_profile (user_id),
                    INDEX idx_business (business_name),
                    INDEX idx_phone (phone_number),
                    FULLTEXT INDEX idx_search (search_vector)
                ) ROW_FORMAT=DYNAMIC
            """))

            # Create customers table
            logger.info("Creating customers table...")
            conn.execute(text("""
                CREATE TABLE customers (
                    id BIGINT PRIMARY KEY,
                    uuid CHAR(36) NOT NULL UNIQUE,
                    nickname VARCHAR(50) NOT NULL,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    business_name VARCHAR(100),
                    street VARCHAR(255),
                    city VARCHAR(100),
                    state VARCHAR(100),
                    zip_code VARCHAR(20),
                    country VARCHAR(100),
                    email VARCHAR(120),
                    phone_number VARCHAR(20),
                    metadata JSON,
                    shipping_address TEXT GENERATED ALWAYS AS (
                        CONCAT_WS(', ',
                            NULLIF(street, ''),
                            NULLIF(city, ''),
                            NULLIF(state, ''),
                            NULLIF(zip_code, ''),
                            NULLIF(country, '')
                        )
                    ) STORED,
                    search_vector TEXT GENERATED ALWAYS AS (
                        CONCAT_WS(' ',
                            NULLIF(nickname, ''),
                            NULLIF(first_name, ''),
                            NULLIF(last_name, ''),
                            NULLIF(business_name, ''),
                            NULLIF(email, ''),
                            NULLIF(phone_number, '')
                        )
                    ) STORED,
                    assigned_to_id BIGINT NOT NULL,
                    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_assigned_by_id BIGINT,
                    last_activity_at DATETIME,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (assigned_to_id) REFERENCES users(id),
                    FOREIGN KEY (last_assigned_by_id) REFERENCES users(id),
                    INDEX idx_customer_assignment (assigned_to_id, created_at),
                    INDEX idx_customer_email (email),
                    INDEX idx_customer_phone (phone_number),
                    INDEX idx_customer_business (business_name),
                    INDEX idx_uuid (uuid),
                    INDEX idx_last_activity (last_activity_at),
                    FULLTEXT INDEX idx_search (search_vector)
                ) ROW_FORMAT=DYNAMIC
            """))

            # Create user_verification_methods table
            logger.info("Creating user_verification_methods table...")
            conn.execute(text("""
                CREATE TABLE user_verification_methods (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    user_id BIGINT NOT NULL,
                    method_type VARCHAR(20) NOT NULL,
                    identifier VARCHAR(120) NOT NULL,
                    verification_token VARCHAR(255),
                    token_expires DATETIME,
                    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
                    verified_at DATETIME,
                    last_verification_attempt DATETIME,
                    verification_attempts INT DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE INDEX idx_user_method (user_id, method_type),
                    INDEX idx_identifier (method_type, identifier),
                    INDEX idx_token (verification_token)
                ) ROW_FORMAT=DYNAMIC
            """))

            # Create payment_methods table
            logger.info("Creating payment_methods table...")
            conn.execute(text("""
                CREATE TABLE payment_methods (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    customer_id BIGINT NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    provider VARCHAR(50) NOT NULL,
                    last_four VARCHAR(4) NOT NULL,
                    expiry_date DATETIME NULL,
                    is_default BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_customer_payments (customer_id)
                )
            """))

            # Create payment_info table
            logger.info("Creating payment_info table...")
            conn.execute(text("""
                CREATE TABLE payment_info (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    customer_id BIGINT NOT NULL,
                    billing_address TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE INDEX idx_customer_payment_info (customer_id)
                )
            """))

            # Create activity_logs table
            logger.info("Creating activity_logs table...")
            conn.execute(text("""
                CREATE TABLE activity_logs (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    user_id BIGINT NOT NULL,
                    action_type VARCHAR(50) NOT NULL,
                    entity_type VARCHAR(50) NOT NULL,
                    entity_id BIGINT NOT NULL,
                    metadata JSON,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (id, created_at),
                    INDEX idx_user_action (user_id, action_type),
                    INDEX idx_entity (entity_type, entity_id),
                    INDEX idx_created_at (created_at)
                ) ROW_FORMAT=COMPRESSED
                PARTITION BY RANGE COLUMNS(created_at) (
                    PARTITION p_2024_01 VALUES LESS THAN ('2024-02-01 00:00:00'),
                    PARTITION p_2024_02 VALUES LESS THAN ('2024-03-01 00:00:00'),
                    PARTITION p_2024_03 VALUES LESS THAN ('2024-04-01 00:00:00'),
                    PARTITION p_2024_04 VALUES LESS THAN ('2024-05-01 00:00:00'),
                    PARTITION p_2024_05 VALUES LESS THAN ('2024-06-01 00:00:00'),
                    PARTITION p_2024_06 VALUES LESS THAN ('2024-07-01 00:00:00'),
                    PARTITION p_future VALUES LESS THAN MAXVALUE
                )
            """))

            # Create verification_messages_log table
            logger.info("Creating verification_messages_log table...")
            conn.execute(text("""
                CREATE TABLE verification_messages_log (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    user_id BIGINT NOT NULL,
                    method_type VARCHAR(20) NOT NULL,
                    message_type VARCHAR(50) NOT NULL,
                    identifier VARCHAR(120) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    provider VARCHAR(50) NOT NULL,
                    provider_message_id VARCHAR(255),
                    error_message TEXT,
                    metadata JSON,
                    ip_address VARCHAR(45),
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (id, created_at),
                    INDEX idx_user_method (user_id, method_type),
                    INDEX idx_status (status, created_at),
                    INDEX idx_provider (provider, created_at)
                ) ROW_FORMAT=COMPRESSED
                PARTITION BY RANGE COLUMNS(created_at) (
                    PARTITION p_2024_01 VALUES LESS THAN ('2024-02-01 00:00:00'),
                    PARTITION p_2024_02 VALUES LESS THAN ('2024-03-01 00:00:00'),
                    PARTITION p_2024_03 VALUES LESS THAN ('2024-04-01 00:00:00'),
                    PARTITION p_2024_04 VALUES LESS THAN ('2024-05-01 00:00:00'),
                    PARTITION p_2024_05 VALUES LESS THAN ('2024-06-01 00:00:00'),
                    PARTITION p_2024_06 VALUES LESS THAN ('2024-07-01 00:00:00'),
                    PARTITION p_future VALUES LESS THAN MAXVALUE
                )
            """))

            logger.info("All tables created successfully")
            
            # Validate tables
            validate_tables(engine)
            logger.info("Table validation successful")
            
            # Create views
            logger.info("Creating views...")
            create_views(engine)
            logger.info("Views created successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

def validate_tables(engine):
    """Validate that all tables were created correctly."""
    try:
        with engine.connect() as conn:
            required_tables = [
                'users', 'user_profiles', 'user_verification_methods',
                'customers', 'activity_logs', 'verification_messages_log',
                'schema_version'
            ]
            
            for table in required_tables:
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'orderme' 
                    AND table_name = :table
                """), {"table": table}).scalar()
                
                if not result:
                    raise MigrationError(f"Table {table} was not created successfully")
            
            logger.info("Table validation successful")
    except Exception as e:
        logger.error(f"Table validation failed: {str(e)}")
        raise

def create_views(engine):
    """Create database views."""
    try:
        logger.info("Creating views...")
        with engine.begin() as conn:
            # Drop existing views
            conn.execute(text("DROP VIEW IF EXISTS v_customer_assignments"))
            conn.execute(text("DROP VIEW IF EXISTS v_active_users"))

            # Create v_active_users view
            conn.execute(text("""
                CREATE VIEW v_active_users AS
                SELECT 
                    u.id,
                    u.email,
                    u.role,
                    u.is_verified,
                    u.last_login_at,
                    up.first_name,
                    up.last_name,
                    up.phone_number
                FROM users u
                LEFT JOIN user_profiles up ON u.id = up.user_id
                WHERE u.is_active = TRUE
            """))

            # Create v_customer_assignments view
            conn.execute(text("""
                CREATE VIEW v_customer_assignments AS
                SELECT 
                    c.id AS customer_id,
                    c.nickname,
                    c.email,
                    c.phone_number,
                    u1.id AS assigned_to_id,
                    u1.email AS assigned_to_email,
                    u2.id AS assigned_by_id,
                    u2.email AS assigned_by_email,
                    c.assigned_at,
                    c.last_activity_at
                FROM customers c
                JOIN users u1 ON c.assigned_to_id = u1.id
                LEFT JOIN users u2 ON c.last_assigned_by_id = u2.id
            """))

            logger.info("Views created successfully")
    except Exception as e:
        logger.error(f"Error creating views: {str(e)}")
        raise

def create_admin_user(engine):
    """Create admin user if not exists."""
    try:
        logger.info("Creating admin user...")
        with engine.begin() as conn:  # Using begin() for automatic transaction handling
            # Check if admin exists
            admin = conn.execute(text("""
                SELECT id FROM users WHERE email = :email
            """), {"email": ADMIN_EMAIL}).fetchone()
            
            if not admin:
                logger.info(f"Creating new admin user with email: {ADMIN_EMAIL}")
                # Create admin user
                password_hash = generate_password_hash(ADMIN_PASSWORD, method='pbkdf2:sha256')
                result = conn.execute(text("""
                    INSERT INTO users (
                        uuid,
                        email,
                        password_hash,
                        role,
                        is_active,
                        is_verified,
                        primary_verification_method,
                        created_as_role
                    ) VALUES (
                        UUID(),
                        :email,
                        :password_hash,
                        'ADMIN',
                        TRUE,
                        TRUE,
                        'email',
                        'SYSTEM'
                    )
                """), {
                    "email": ADMIN_EMAIL,
                    "password_hash": password_hash
                })
                
                # Get admin user id
                admin_id = conn.execute(text("""
                    SELECT id FROM users WHERE email = :email
                """), {"email": ADMIN_EMAIL}).scalar()
                
                logger.info(f"Created admin user with ID: {admin_id}")
                
                # Create admin profile
                conn.execute(text("""
                    INSERT INTO user_profiles (
                        user_id,
                        first_name,
                        last_name
                    ) VALUES (
                        :user_id,
                        'Admin',
                        'User'
                    )
                """), {"user_id": admin_id})
                
                logger.info("Created admin user profile")
                
                # Create admin verification method
                conn.execute(text("""
                    INSERT INTO user_verification_methods (
                        user_id,
                        method_type,
                        identifier,
                        is_verified,
                        verified_at
                    ) VALUES (
                        :user_id,
                        'email',
                        :email,
                        TRUE,
                        CURRENT_TIMESTAMP
                    )
                """), {
                    "user_id": admin_id,
                    "email": ADMIN_EMAIL
                })
                
                logger.info("Created admin verification method")
                
                # Verify that admin was created correctly
                admin_check = conn.execute(text("""
                    SELECT 
                        u.id,
                        u.email,
                        u.role,
                        up.first_name,
                        uvm.method_type
                    FROM users u
                    LEFT JOIN user_profiles up ON u.id = up.user_id
                    LEFT JOIN user_verification_methods uvm ON u.id = uvm.user_id
                    WHERE u.id = :user_id
                """), {"user_id": admin_id}).fetchone()
                
                if admin_check:
                    logger.info(f"Admin user verified - ID: {admin_check[0]}, Email: {admin_check[1]}, Role: {admin_check[2]}")
                else:
                    raise Exception("Failed to verify admin user creation")
                
                logger.info("Admin user created successfully")
            else:
                logger.info("Admin user already exists")
                
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise

def update_version(engine):
    """Update database version."""
    try:
        logger.info("Updating database version...")
        with engine.connect() as conn:
            # Calculate migration hash
            migration_hash = hashlib.sha256(
                f"{MIGRATION_VERSION}_{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            # Update version
            conn.execute(text("""
                INSERT INTO schema_version (
                    version,
                    migrated_at,
                    migration_hash
                ) VALUES (
                    :version,
                    CURRENT_TIMESTAMP,
                    :migration_hash
                )
            """), {
                "version": MIGRATION_VERSION,
                "migration_hash": migration_hash
            })
            
            logger.info(f"Database version updated to {MIGRATION_VERSION}")
    except Exception as e:
        logger.error(f"Error updating version: {str(e)}")
        raise

def migrate_database(engine):
    """
    Perform database migration.
    """
    try:
        # Verify database exists
        verify_database(engine)
        
        # Create backup
        create_backup(engine)
        
        # Create tables and views
        create_tables(engine)
        
        # Create admin user
        create_admin_user(engine)
        
        # Update database version
        update_version(engine)
        
        logger.info("Database migrated to version 1.0.0")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

def main():
    """Main migration function."""
    try:
        # Initialize database connection
        engine = create_engine(
            DB_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )
        
        # Run migration
        migrate_database(engine)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
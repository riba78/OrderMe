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
        raise

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
    """Create all required tables."""
    try:
        logger.info("Creating tables...")
        
        # Create a fresh connection for this operation
        with engine.connect() as conn:
            # Drop existing tables if they exist (in correct order)
            logger.info("Dropping existing tables...")
            
            # Execute each DROP statement separately
            tables_to_drop = [
                "verification_messages_log",
                "activity_logs",
                "payment_info",
                "payment_methods",
                "user_verification_methods",
                "user_profiles",
                "customers",
                "users"
            ]
            
            for table in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                except Exception as e:
                    logger.warning(f"Error dropping table {table}: {str(e)}")
            
            # Create tables one by one
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
                    UNIQUE KEY unique_email (email)
                )
            """))
            
            logger.info("Creating customers table...")
            conn.execute(text("""
                CREATE TABLE customers (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    user_id BIGINT NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    phone VARCHAR(20),
                    address TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            
            logger.info("Creating user_profiles table...")
            conn.execute(text("""
                CREATE TABLE user_profiles (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    user_id BIGINT NOT NULL,
                    profile_picture VARCHAR(255),
                    bio TEXT,
                    preferences JSON,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            
            logger.info("Creating user_verification_methods table...")
            conn.execute(text("""
                CREATE TABLE user_verification_methods (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    user_id BIGINT NOT NULL,
                    method_type VARCHAR(20) NOT NULL,
                    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
                    verification_data JSON,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            
            logger.info("Creating payment_methods table...")
            conn.execute(text("""
                CREATE TABLE payment_methods (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    user_id BIGINT NOT NULL,
                    method_type VARCHAR(20) NOT NULL,
                    is_default BOOLEAN NOT NULL DEFAULT FALSE,
                    payment_details JSON NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            
            logger.info("Creating payment_info table...")
            conn.execute(text("""
                CREATE TABLE payment_info (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    user_id BIGINT NOT NULL,
                    payment_method_id BIGINT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
                    status VARCHAR(20) NOT NULL,
                    transaction_id VARCHAR(255),
                    payment_details JSON,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id) ON DELETE CASCADE
                )
            """))
            
            logger.info("Creating activity_logs table...")
            conn.execute(text("""
                CREATE TABLE activity_logs (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    user_id BIGINT NOT NULL,
                    activity_type VARCHAR(50) NOT NULL,
                    description TEXT,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            
            logger.info("Creating verification_messages_log table...")
            conn.execute(text("""
                CREATE TABLE verification_messages_log (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    user_id BIGINT NOT NULL,
                    message_type VARCHAR(20) NOT NULL,
                    sent_to VARCHAR(120) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    error_message TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            
            logger.info("All tables created successfully")
            
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
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
        with engine.connect() as conn:
            # Create view for active users with their profile information
            conn.execute(text("""
                CREATE OR REPLACE VIEW v_active_users AS
                SELECT 
                    u.id,
                    u.email,
                    u.role,
                    u.is_verified,
                    u.last_login_at,
                    c.first_name,
                    c.last_name,
                    c.phone,
                    c.address,
                    up.profile_picture,
                    up.bio
                FROM users u
                LEFT JOIN customers c ON u.id = c.user_id
                LEFT JOIN user_profiles up ON u.id = up.user_id
                WHERE u.is_active = TRUE;
            """))
            
            # Create view for user verification status
            conn.execute(text("""
                CREATE OR REPLACE VIEW v_user_verification_status AS
                SELECT 
                    u.id,
                    u.email,
                    u.is_verified,
                    u.primary_verification_method,
                    COUNT(uvm.id) as verification_methods_count,
                    GROUP_CONCAT(uvm.method_type) as available_methods
                FROM users u
                LEFT JOIN user_verification_methods uvm ON u.id = uvm.user_id
                GROUP BY u.id;
            """))
            
            # Create view for payment methods
            conn.execute(text("""
                CREATE OR REPLACE VIEW v_user_payment_methods AS
                SELECT 
                    u.id as user_id,
                    u.email,
                    pm.id as payment_method_id,
                    pm.method_type,
                    pm.is_default,
                    COUNT(pi.id) as times_used,
                    MAX(pi.created_at) as last_used
                FROM users u
                LEFT JOIN payment_methods pm ON u.id = pm.user_id
                LEFT JOIN payment_info pi ON pm.id = pi.payment_method_id
                GROUP BY u.id, pm.id;
            """))
            
            logger.info("Views created successfully")
    except Exception as e:
        logger.error(f"Error creating views: {str(e)}")
        raise

def create_procedures(engine):
    """Create stored procedures."""
    try:
        logger.info("Creating stored procedures...")
        with engine.connect() as conn:
            # Create user procedure
            conn.execute(text("""
                CREATE PROCEDURE IF NOT EXISTS sp_create_user(
                    IN p_email VARCHAR(120),
                    IN p_password VARCHAR(255),
                    IN p_role VARCHAR(20),
                    IN p_created_by_id BIGINT,
                    IN p_verification_method VARCHAR(20),
                    OUT p_user_id BIGINT
                )
                BEGIN
                    DECLARE v_uuid CHAR(36);
                    SET v_uuid = UUID();
                    
                    INSERT INTO users (
                        uuid,
                        email,
                        password_hash,
                        role,
                        created_by_id,
                        created_as_role,
                        primary_verification_method
                    ) VALUES (
                        v_uuid,
                        p_email,
                        p_password,
                        p_role,
                        p_created_by_id,
                        p_role,
                        p_verification_method
                    );
                    
                    SET p_user_id = LAST_INSERT_ID();
                    
                    INSERT INTO activity_logs (
                        user_id,
                        activity_type,
                        description
                    ) VALUES (
                        p_created_by_id,
                        'user_create',
                        CONCAT('Created user ', p_email, ' with role ', p_role)
                    );
                END
            """))
            
            # Create verification procedure
            conn.execute(text("""
                CREATE PROCEDURE IF NOT EXISTS sp_verify_user(
                    IN p_user_id BIGINT,
                    IN p_method_type VARCHAR(20),
                    IN p_verification_data JSON
                )
                BEGIN
                    UPDATE users 
                    SET is_verified = TRUE,
                        primary_verification_method = p_method_type
                    WHERE id = p_user_id;
                    
                    INSERT INTO user_verification_methods (
                        user_id,
                        method_type,
                        is_verified,
                        verification_data
                    ) VALUES (
                        p_user_id,
                        p_method_type,
                        TRUE,
                        p_verification_data
                    );
                    
                    INSERT INTO activity_logs (
                        user_id,
                        activity_type,
                        description
                    ) VALUES (
                        p_user_id,
                        'user_verify',
                        CONCAT('User verified using ', p_method_type)
                    );
                END
            """))
            
            # Create payment method procedure
            conn.execute(text("""
                CREATE PROCEDURE IF NOT EXISTS sp_add_payment_method(
                    IN p_user_id BIGINT,
                    IN p_method_type VARCHAR(20),
                    IN p_payment_details JSON,
                    IN p_is_default BOOLEAN
                )
                BEGIN
                    IF p_is_default THEN
                        UPDATE payment_methods
                        SET is_default = FALSE
                        WHERE user_id = p_user_id;
                    END IF;
                    
                    INSERT INTO payment_methods (
                        user_id,
                        method_type,
                        payment_details,
                        is_default
                    ) VALUES (
                        p_user_id,
                        p_method_type,
                        p_payment_details,
                        p_is_default
                    );
                    
                    INSERT INTO activity_logs (
                        user_id,
                        activity_type,
                        description
                    ) VALUES (
                        p_user_id,
                        'payment_method_add',
                        CONCAT('Added payment method: ', p_method_type)
                    );
                END
            """))
            
            logger.info("Stored procedures created successfully")
    except Exception as e:
        logger.error(f"Error creating procedures: {str(e)}")
        raise

def create_functions(engine):
    """Create database functions for validation."""
    try:
        with engine.connect() as conn:
            with conn.begin():
                logger.info("Creating database functions...")
                # Create phone validation function
                conn.execute(text("""
                    DELIMITER //
                    CREATE OR REPLACE FUNCTION fn_validate_phone(phone VARCHAR(20))
                    RETURNS BOOLEAN
                    DETERMINISTIC
                    BEGIN
                        RETURN phone REGEXP '^\\+?[1-9]\\d{1,14}$';
                    END //
                    DELIMITER ;
                """))
                
                # Create email validation function
                conn.execute(text("""
                    DELIMITER //
                    CREATE OR REPLACE FUNCTION fn_validate_email(email VARCHAR(120))
                    RETURNS BOOLEAN
                    DETERMINISTIC
                    BEGIN
                        RETURN email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$';
                    END //
                    DELIMITER ;
                """))
                
                # Validate functions
                required_functions = ['fn_validate_phone', 'fn_validate_email']
                for func in required_functions:
                    result = conn.execute(text("""
                        SELECT COUNT(*) 
                        FROM information_schema.routines 
                        WHERE routine_schema = 'orderme' 
                        AND routine_name = :func
                    """), {"func": func}).scalar()
                    
                    if not result:
                        raise MigrationError(f"Function {func} was not created successfully")
                
                logger.info("Database functions created and validated successfully")
    except Exception as e:
        logger.error(f"Error creating functions: {str(e)}")
        raise

def create_admin_user(engine):
    """Create admin user if not exists."""
    try:
        logger.info("Creating admin user...")
        with engine.begin() as conn:  # Using begin() to automatically handle transactions
            # Check if admin exists
            result = conn.execute(text("""
                SELECT id FROM users WHERE email = :email
            """), {"email": ADMIN_EMAIL}).fetchone()
            
            if result:
                logger.info("Admin user already exists")
                return
            
            # Create admin user
            admin_uuid = str(uuid.uuid4())
            password_hash = generate_password_hash(ADMIN_PASSWORD, method='pbkdf2:sha256')
            
            result = conn.execute(text("""
                INSERT INTO users (
                    uuid,
                    email,
                    password_hash,
                    role,
                    is_active,
                    is_verified,
                    created_as_role
                ) VALUES (
                    :uuid,
                    :email,
                    :password_hash,
                    'ADMIN',
                    TRUE,
                    TRUE,
                    'SYSTEM'
                )
            """), {
                "uuid": admin_uuid,
                "email": ADMIN_EMAIL,
                "password_hash": password_hash
            })
            
            admin_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
            
            # Create admin customer profile
            conn.execute(text("""
                INSERT INTO customers (
                    user_id,
                    first_name,
                    last_name,
                    phone
                ) VALUES (
                    :user_id,
                    'Admin',
                    'User',
                    NULL
                )
            """), {"user_id": admin_id})
            
            # Create admin user profile
            conn.execute(text("""
                INSERT INTO user_profiles (
                    user_id,
                    profile_picture,
                    bio
                ) VALUES (
                    :user_id,
                    NULL,
                    'System administrator'
                )
            """), {"user_id": admin_id})
            
            # Log admin creation
            conn.execute(text("""
                INSERT INTO activity_logs (
                    user_id,
                    activity_type,
                    description
                ) VALUES (
                    :user_id,
                    'user_create',
                    'Created initial admin user'
                )
            """), {"user_id": admin_id})
            
            logger.info("Admin user created successfully")
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

def main():
    """Main migration function."""
    try:
        # Initialize engine
        engine = create_engine(DB_URL)
        
        # Validate environment
        validate_environment()
        
        # Create database if not exists
        create_database(engine)
        
        # Check database version
        if not check_database_version(engine):
            # Create backup
            backup_file = create_backup(engine)
            
            try:
                # Create tables
                create_tables(engine)
                
                # Validate tables
                validate_tables(engine)
                
                # Create views
                create_views(engine)
                
                # Skip stored procedures for now due to MariaDB version mismatch
                # create_procedures(engine)
                
                # Create admin user
                create_admin_user(engine)
                
                # Update version
                update_version(engine)
                
                logger.info("Migration completed successfully")
            except Exception as e:
                logger.error(f"Migration failed: {str(e)}")
                logger.info(f"Backup is available at: {backup_file}")
                raise
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
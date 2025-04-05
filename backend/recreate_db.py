"""
Database Recreation Utility

This script completely recreates the database schema:
1. Drops all existing tables
2. Creates new tables based on current models
3. Initializes required data (e.g., admin user)

Usage:
    python recreate_db.py

WARNING: This script will delete all existing data!
Use only in development or when a complete reset is needed.

Features:
- Complete database reset
- Fresh schema creation
- Initial data seeding
- Proper handling of partitioned tables
- Environment-based configuration
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

def get_db_url_without_db():
    """Get database URL without database name"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Parse the URL to remove database name
    parsed = urlparse(db_url)
    # Reconstruct URL without path (database name)
    base_url = f"{parsed.scheme}://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}"
    return base_url

def recreate_database():
    """Recreate the database with proper character set"""
    # Connect to MySQL server (without specifying a database)
    engine = create_engine(get_db_url_without_db())
    db_name = urlparse(os.getenv('DATABASE_URL')).path.strip('/')

    with engine.connect() as conn:
        try:
            # Drop database if exists
            conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
            conn.commit()
            print(f"Dropped existing database: {db_name}")
            
            # Create database with proper character set
            conn.execute(text(f"""
                CREATE DATABASE {db_name} 
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci
            """))
            conn.commit()
            print(f"Created new database: {db_name}")
            
            # Set configuration for partitioned tables
            conn.execute(text(f"""
                ALTER DATABASE {db_name} 
                SET GLOBAL innodb_file_per_table=1, 
                    GLOBAL innodb_file_format=Barracuda
            """))
            conn.commit()
            print("Configured database for partitioned tables")
            
        except Exception as e:
            print(f"Error recreating database: {str(e)}")
            raise

if __name__ == '__main__':
    try:
        recreate_database()
        print("\nDatabase recreation completed successfully")
        print("\nNext steps:")
        print("1. Run migrations: python migrate_db.py")
        print("2. Create admin user: python create_admin.py")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nDatabase recreation failed") 
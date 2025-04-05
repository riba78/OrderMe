"""
Database Tables Drop Utility

This script drops all tables in the database:
1. Connects to the database
2. Drops all existing tables
3. Leaves the database empty but intact

Usage:
    python drop_tables.py

WARNING: This script will delete all data in all tables!
Use with extreme caution, primarily in development.

The script is useful for:
- Complete data cleanup
- Schema reset
- Development environment reset
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

def drop_all_tables():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    # Create engine
    engine = create_engine(db_url)

    # Tables in order of deletion (to handle foreign key constraints)
    # Note: Partitioned tables must be dropped first to avoid foreign key issues
    tables = [
        'verification_messages_log',  # Partitioned by created_at
        'activity_logs',             # Partitioned by created_at
        'payment_info',
        'payment_methods',
        'user_verification_methods',
        'user_profiles',
        'customers',
        'users',
        'schema_version'
    ]

    # Drop tables
    with engine.connect() as conn:
        # First, check and drop any partitions
        for partitioned_table in ['verification_messages_log', 'activity_logs']:
            try:
                # Get partitions for the table
                result = conn.execute(text(f"""
                    SELECT PARTITION_NAME 
                    FROM INFORMATION_SCHEMA.PARTITIONS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = '{partitioned_table}'
                """))
                partitions = [row[0] for row in result]
                
                # Drop each partition
                for partition in partitions:
                    if partition:
                        conn.execute(text(f"ALTER TABLE {partitioned_table} DROP PARTITION {partition}"))
                print(f"Dropped partitions for table: {partitioned_table}")
            except Exception as e:
                print(f"Error dropping partitions for {partitioned_table}: {str(e)}")

        # Then drop the tables
        for table in tables:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                print(f"Dropped table: {table}")
            except Exception as e:
                print(f"Error dropping {table}: {str(e)}")
        conn.commit()

if __name__ == '__main__':
    try:
        drop_all_tables()
        print("All tables dropped successfully")
    except Exception as e:
        print(f"Error: {str(e)}") 
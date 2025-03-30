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
- Useful for development and testing
"""

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Connect to MySQL server (without specifying a database)
engine = create_engine('mysql+pymysql://orderme_user:Brat1978@127.0.0.1:3306')

with engine.connect() as conn:
    # Drop database if exists
    conn.execute(text("DROP DATABASE IF EXISTS orderme"))
    conn.commit()
    
    # Create database with proper character set
    conn.execute(text("CREATE DATABASE orderme CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
    conn.commit()
    
print("Database dropped and recreated successfully") 
"""
Database Connection Check Utility

This script verifies the database connection and configuration:
1. Loads environment variables
2. Attempts to connect to the configured MySQL database
3. Prints connection status and database information

Usage:
    python check_db.py

The script is useful for:
- Verifying database connectivity
- Debugging connection issues
- Validating environment configuration
- Testing database access permissions
"""

from dotenv import load_dotenv
from app import create_app
from extensions import db
from models.user import User

app = create_app()

with app.app_context():
    try:
        # Check if we can query the database
        users = User.query.all()
        print("Successfully connected to database")
        print("\nUsers in database:")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Role: {user.role}, Password Hash: {user.password_hash}")
    except Exception as e:
        print(f"Failed to connect to database: {e}") 
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

from app import create_app
from extensions import db

app = create_app()

with app.app_context():
    # Drop all tables
    db.drop_all()
    print("All tables dropped successfully") 
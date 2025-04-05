"""Script to drop all views from the database."""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://orderme_user:Brat1978@127.0.0.1:3306/orderme')

def drop_views():
    """Drop all views from the database."""
    try:
        # Create database engine
        engine = create_engine(DB_URL)
        
        with engine.connect() as conn:
            # Get all views
            views = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = 'orderme'
            """)).fetchall()
            
            # Drop each view
            for view in views:
                view_name = view[0]
                conn.execute(text(f"DROP VIEW IF EXISTS {view_name}"))
                print(f"Dropped view: {view_name}")
            
            print("All views dropped successfully")
            
    except Exception as e:
        print(f"Error dropping views: {str(e)}")
        raise

if __name__ == '__main__':
    drop_views() 
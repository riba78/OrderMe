from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

# Get database URL from environment
db_url = os.getenv('DATABASE_URL')
print(f"Using database URL: {db_url}")

try:
    # Create engine
    engine = create_engine(db_url)
    
    # Test connection
    with engine.connect() as conn:
        # Try to execute a simple query
        result = conn.execute(text("SELECT 1"))
        print("Successfully connected to database!")
        print(f"Query result: {result.scalar()}")
        
        # Try to get database name
        db_name = conn.execute(text("SELECT DATABASE()")).scalar()
        print(f"Connected to database: {db_name}")
        
except Exception as e:
    print(f"Failed to connect to database: {str(e)}") 
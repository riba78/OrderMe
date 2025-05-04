# Test both environments
#python3 -m app.check_connection

# Or test specific environment using environment variable
#ENV=development python3 -m app.check_connection
#ENV=production python3 -m app.check_connection#

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

# Load environment variables
load_dotenv()

async def test_connection(env: str = "development"):
    """Test database connection for specified environment."""
    try:
        # Get appropriate DATABASE_URL based on environment
        if env == "production":
            DATABASE_URL = os.getenv("DATABASE_URL_PROD")
            print(f"Testing PRODUCTION database connection...")
        else:
            DATABASE_URL = os.getenv("DATABASE_URL_DEV")
            print(f"Testing DEVELOPMENT database connection...")

        if not DATABASE_URL:
            raise ValueError(f"No database URL found for {env} environment")

        # Create test engine with same configuration as in database.py
        engine = create_async_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            connect_args={
                "ssl": {"ssl_ca": "/Applications/XAMPP/xamppfiles/phpmyadmin/DigiCertGlobalRootCA.crt.pem"}
            }
        )

        # Try to connect and execute a simple query
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            await conn.execute(text("SHOW DATABASES"))
            databases = await conn.execute(text("SHOW DATABASES"))
            print("\nAvailable databases:")
            for row in databases.fetchall():
                print(f"- {row[0]}")
            
            # Test specific database access
            current_db = await conn.execute(text("SELECT DATABASE()"))
            db_name = current_db.first()[0]
            print(f"\nCurrently connected to: {db_name}")

            # Test tables in current database
            tables = await conn.execute(text("SHOW TABLES"))
            print("\nAvailable tables:")
            for row in tables.fetchall():
                print(f"- {row[0]}")

        print("\n✅ Connection successful!")
        return True

    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        return False

    finally:
        if 'engine' in locals():
            await engine.dispose()

async def main():
    """Test both development and production connections."""
    print("\n=== Database Connection Test ===\n")
    
    # Test development connection
    await test_connection("development")
    
    print("\n" + "="*30 + "\n")
    
    # Test production connection
    await test_connection("production")

if __name__ == "__main__":
    asyncio.run(main())
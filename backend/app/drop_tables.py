# run from backend directory: python3 -m app.drop_tables

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env in the backend root
load_dotenv()

# Import Base and all models to ensure all tables are registered
from app.models import Base  # models/__init__.py imports all models
from app.database import engine  # Use the already configured engine

async def drop_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("All tables dropped!")

if __name__ == "__main__":
    asyncio.run(drop_all_tables())
    
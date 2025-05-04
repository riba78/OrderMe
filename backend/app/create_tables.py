#run from backend python3 -m app.create_tables

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env in the backend root
load_dotenv()

# Import Base and all models to ensure all tables are registered
from app.models import Base  # models/__init__.py imports all models
from app.database import engine  # Use the already configured engine

async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created!")

if __name__ == "__main__":
    asyncio.run(create_all_tables())

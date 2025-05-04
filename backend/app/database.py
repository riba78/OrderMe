"""
Key Features:
- Asynchronous database connection
- Dependency injection for database sessions
- Connection pooling and recycling
- SSL/TLS certificate handling
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

ENV = os.getenv("ENV", "development")  # default to development

if ENV == "production":
    DATABASE_URL = os.getenv("DATABASE_URL_PROD")
else:
    DATABASE_URL = os.getenv("DATABASE_URL_DEV")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    connect_args={
        "ssl": {"ssl_ca": "/Applications/XAMPP/xamppfiles/phpmyadmin/DigiCertGlobalRootCA.crt.pem"}
    }
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        yield session




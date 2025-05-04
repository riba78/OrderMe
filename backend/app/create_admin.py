# run from backend: python3 -m app.create_admin
# run backend server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# python3 -m uvicorn app.main:app --reload

import asyncio
import os
import uuid
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User, UserRole
from app.models.admin_manager import AdminManager, VerificationMethod
from app.database import engine, AsyncSessionLocal
from app.utils.security import hash_password

# Load environment variables from .env in the backend root
load_dotenv()

ADMIN_EMAIL = "admin@orderme.com"
ADMIN_PASSWORD = "admin123"  # You can change this or prompt for input
TIN_TRUNK_NUMBER = "123456789"
VERIFICATION_METHOD = VerificationMethod.email

async def create_admin_user():
    async with AsyncSessionLocal() as session:
        session: AsyncSession = session
        
        # Create admin user
        admin = User(
            role=UserRole.admin,
            is_active=True
        )
        session.add(admin)
        await session.flush()  # This will assign an ID to admin

        # Create admin credentials
        admin_manager = AdminManager(
            id=admin.id,
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            tin_trunk_number=TIN_TRUNK_NUMBER,
            verification_method=VERIFICATION_METHOD
        )
        session.add(admin_manager)
        
        await session.commit()
        print(f"Admin user created successfully with email: {ADMIN_EMAIL}")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
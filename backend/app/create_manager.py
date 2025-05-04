# run from backend: python3 -m app.create_manager

import asyncio
import os
import uuid
from dotenv import load_dotenv
from sqlalchemy.future import select

from app.models import User, UserRole
from app.models.admin_manager import AdminManager, VerificationMethod
from app.database import AsyncSessionLocal
from app.utils.security import hash_password

# Load environment variables from .env in the backend root
load_dotenv()

MANAGER_EMAIL = "manager@orderme.com"
MANAGER_PASSWORD = "manager123"
TIN_TRUNK_NUMBER = "123456"
VERIFICATION_METHOD = VerificationMethod.email

async def create_manager():
    async with AsyncSessionLocal() as session:
        # Check if manager already exists
        result = await session.execute(
            select(AdminManager).where(AdminManager.email == MANAGER_EMAIL)
        )
        existing_manager = result.scalar_one_or_none()
        if existing_manager:
            print(f"Manager with email {MANAGER_EMAIL} already exists.")
            return

        # Create User
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            role=UserRole.manager,
            is_active=True
        )
        session.add(user)
        await session.flush()  # Ensure user is inserted before using FK

        # Create AdminManager
        admin_manager = AdminManager(
            id=user_id,  # Use same UUID as user for 1:1 relationship
            email=MANAGER_EMAIL,
            password_hash=hash_password(MANAGER_PASSWORD),
            tin_trunk_number=TIN_TRUNK_NUMBER,
            verification_method=VERIFICATION_METHOD
        )
        session.add(admin_manager)
        await session.commit()
        print(f"Manager user {MANAGER_EMAIL} created successfully.")

if __name__ == "__main__":
    asyncio.run(create_manager())
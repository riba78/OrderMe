# run from backend: python3 -m app.create_customer

import asyncio
import os
import uuid
from dotenv import load_dotenv
from sqlalchemy.future import select

from app.models import User
from app.models.customer import Customer
from app.database import AsyncSessionLocal

# Load environment variables from .env in the backend root
load_dotenv()

CUSTOMER_PHONE = "999123567"
CREATOR_EMAIL = "manager@orderme.com"  # Change as needed
ASSIGNED_MANAGER_EMAIL = None  # Set to an email or None

async def create_customer():
    async with AsyncSessionLocal() as session:
        # Check if customer already exists
        result = await session.execute(
            select(Customer).where(Customer.phone == CUSTOMER_PHONE)
        )
        existing_customer = result.scalar_one_or_none()
        if existing_customer:
            print(f"Customer with phone {CUSTOMER_PHONE} already exists.")
            return

        # Find creator user
        result = await session.execute(
            select(User).where(User.admin_manager.has(email=CREATOR_EMAIL))
        )
        creator = result.scalar_one_or_none()
        if not creator:
            print(f"Creator user with email {CREATOR_EMAIL} not found.")
            return

        # Find assigned manager user (optional)
        assigned_manager_id = None
        if ASSIGNED_MANAGER_EMAIL:
            result = await session.execute(
                select(User).where(User.admin_manager.has(email=ASSIGNED_MANAGER_EMAIL))
            )
            assigned_manager = result.scalar_one_or_none()
            if not assigned_manager:
                print(f"Assigned manager with email {ASSIGNED_MANAGER_EMAIL} not found.")
                return
            assigned_manager_id = assigned_manager.id

        # Create Customer
        customer = Customer(
            id=str(uuid.uuid4()),
            phone=CUSTOMER_PHONE,
            created_by=creator.id,
            assigned_manager_id=assigned_manager_id
        )
        session.add(customer)
        await session.commit()
        print(f"Customer with phone {CUSTOMER_PHONE} created successfully.")

if __name__ == "__main__":
    asyncio.run(create_customer())
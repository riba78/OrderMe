# Implements the 'IUserRepository' using a generic 'AsyncCrudRepository' for boilerplate CRUD methods.

from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models.user import User, UserRole
from ..models.admin_manager import AdminManager
from ..schemas.user import UserCreate, UserUpdate
from ..schemas.admin_manager import AdminManagerCreate
from .interfaces.user_repository import IUserRepository
from .async_crud import AsyncCrudRepository
from ..utils.security import hash_password
from ..models.admin_manager import VerificationMethod
import logging # Temporary
from sqlalchemy.dialects import mysql # Or postgresql, sqlite, etc.

class UserRepository(
    AsyncCrudRepository[User, UserCreate, UserUpdate],
    IUserRepository
):
    '''Concrete repository for User, utilizing AsyncCrudRepository for core methods'''
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def find_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.admin_manager))
            .where(User.admin_manager.has(email=email))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def find_by_phone(self, phone: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.admin_manager))
            .where(User.admin_manager.has(phone=phone))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def create_user_with_credentials(self, creds: AdminManagerCreate) -> User:
        """
        Create a new user with manager role and associated admin manager credentials.
        
        Args:
            creds: AdminManagerCreate schema with email, password, verification_method fields
            
        Returns:
            User: Newly created user with manager role
        """
        # Create a new user with manager role by default
        user = User(
            role=UserRole.manager,
            is_active=True
        )
        self.session.add(user)
        await self.session.flush()  # Assign ID to user
        
        # Create admin_manager credentials linked to the user
        if not creds.verification_method:
            creds.verification_method = VerificationMethod.email
        admin_manager = AdminManager(
            id=user.id,
            email=creds.email,
            password_hash=hash_password(creds.password),
            verification_method=creds.verification_method,
            tin_trunk_number=creds.tin_trunk_number
        )
        self.session.add(admin_manager)
        
        await self.session.commit()
        await self.session.refresh(user)
        return user
        
    async def list_all(self) -> list[User]:
        stmt = (
            select(User)
            .options(
                selectinload(User.admin_manager),
                selectinload(User.customer)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, id: uuid.UUID) -> Optional[User]:
        stmt = (
            select(self.model)
            .options(
                selectinload(User.admin_manager),
                selectinload(User.customer)
            )
            .where(self.model.id == str(id))
        )
        
        # For logging the compiled query with literal binds
        compiled_stmt_str = str(stmt.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))
        logging.warning(f"UserRepository.get_by_id: Attempting to find user with ID_str: {str(id)}")
        logging.warning(f"UserRepository.get_by_id: Compiled SQL: {compiled_stmt_str}")

        result = await self.session.execute(stmt)
        user = result.scalars().first()
        logging.warning(f"UserRepository.get_by_id: User found from DB: {user}")
        return user

    async def update(self, id: uuid.UUID, data: UserUpdate) -> Optional[User]:
        user_to_update = await self.get_by_id(id)
        if not user_to_update:
            return None

        updated_fields = False
        models_to_add_to_session = {user_to_update}

        # Update fields on the User model itself
        if data.role is not None and user_to_update.role != data.role:
            user_to_update.role = data.role
            updated_fields = True
        if data.is_active is not None and user_to_update.is_active != data.is_active:
            user_to_update.is_active = data.is_active
            updated_fields = True

        # Handle email and phone based on role
        if user_to_update.role == UserRole.customer:
            if data.phone is not None:
                if user_to_update.customer:
                    if user_to_update.customer.phone != data.phone:
                        user_to_update.customer.phone = data.phone
                        models_to_add_to_session.add(user_to_update.customer)
                        updated_fields = True
                else:
                    # This case (customer role without a customer record) should ideally not happen
                    # if customer records are created when role is set to customer.
                    # Depending on business logic, you might create one here or log an error.
                    # For now, we'll assume customer record exists if role is customer.
                    pass 
            # Customers typically don't have their email updated via this general endpoint directly
            # as their primary contact is phone. If User model has an email field for all users,
            # and it's intended to be updatable for customers too, that logic would go here.
            # Based on UserTable, email is not sent for customers.

        elif user_to_update.role in [UserRole.admin, UserRole.manager]:
            if user_to_update.admin_manager:
                if data.email is not None and user_to_update.admin_manager.email != data.email:
                    user_to_update.admin_manager.email = data.email
                    models_to_add_to_session.add(user_to_update.admin_manager)
                    updated_fields = True
                # If admins/managers can also have a phone number on their AdminManager profile:
                # if data.phone is not None and hasattr(user_to_update.admin_manager, 'phone') and \
                #    user_to_update.admin_manager.phone != data.phone:
                #     user_to_update.admin_manager.phone = data.phone
                #     models_to_add_to_session.add(user_to_update.admin_manager)
                #     updated_fields = True
            elif data.email is not None :
                # Admin/Manager role without an admin_manager record - should not happen.
                pass
        
        # Fallback for a generic User.email or User.phone if they exist directly on User model
        # and are not handled by role-specific logic above (unlikely given current structure)
        # Example:
        # if data.email is not None and hasattr(user_to_update, 'email') and user_to_update.email != data.email and not user_to_update.admin_manager:
        #     user_to_update.email = data.email # If User model itself has an email field
        #     updated_fields = True


        if updated_fields:
            for model_instance in models_to_add_to_session:
                self.session.add(model_instance)
            await self.session.commit()
            await self.session.refresh(user_to_update)
            if user_to_update.admin_manager in models_to_add_to_session:
                await self.session.refresh(user_to_update.admin_manager)
            if user_to_update.customer in models_to_add_to_session:
                await self.session.refresh(user_to_update.customer)
        
        return user_to_update

    # The following methods are inherited from AsyncCrudRepository:
    # - create
    # - get_by_id
    # - update
    # - delete
    
    
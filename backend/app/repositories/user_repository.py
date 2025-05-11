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

    # The following methods are inherited from AsyncCrudRepository:
    # - create
    # - get_by_id
    # - update
    # - delete
    
    
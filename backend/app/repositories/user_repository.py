# Implements the 'IUserRepository' using a generic 'AsyncCrudRepository' for boilerplate CRUD methods.

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from .interfaces.user_repository import IUserRepository
from .async_crud import AsyncCrudRepository

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
        
    # The following methods are inherited from AsyncCrudRepository:
    # - create
    # - get_by_id
    # - update
    # - delete
    # - list_all
    
    
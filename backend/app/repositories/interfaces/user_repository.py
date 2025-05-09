# abstract interface defining async CRUD and lookup methods for users.

from abc import ABC, abstractmethod
from typing import List, Optional
from ...models import User
from ...schemas import UserCreate, UserResponse
from ...schemas.admin_manager import AdminManagerCreate

class IUserRepository(ABC):
    """Abstract interface for async CRUD and lookup methods on User entities."""

    @abstractmethod
    async def create(self, user_data: UserCreate) -> User:
        pass 

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def update(self, id: str, user_data: UserCreate) -> User:
        pass

    @abstractmethod
    async def delete(self, id: str) -> None:
        pass

    @abstractmethod
    async def list_all(self) -> List[User]:
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def find_by_phone(self, phone: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create_user_with_credentials(self, creds: AdminManagerCreate) -> User:
        pass




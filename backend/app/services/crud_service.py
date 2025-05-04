# generic service providing async create, read, update, delete, and list operations.

from typing import Optional, TypeVar, Generic, List
from ..repositories.interfaces.user_repository import IUserRepository

ModelType = TypeVar("ModelType")
CreateType = TypeVar("CreateType")
UpdateType = TypeVar("UpdateType")

class CRUDService(Generic[ModelType, CreateType, UpdateType]):
    """Base class for async CRUD services."""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def create(self, data: CreateType) -> ModelType:
        return await self.repository.create(data)
    
    async def get(self, id: str) -> ModelType:
        return await self.repository.get_by_id(id)
    
    async def update(self, id: str, data: UpdateType) -> ModelType:
        return await self.repository.update(id, data)
    
    async def delete(self, id: str) -> None:
        await self.repository.delete(id)

    async def list_all(self) -> List[ModelType]:
        return await self.repository.list_all()
    
    async def find_by_email(self, email: str) -> Optional[ModelType]:
        return await self.repository.find_by_email(email)
    
    async def find_by_phone(self, phone: str) -> Optional[ModelType]:
        return await self.repository.find_by_phone(phone)
    
    
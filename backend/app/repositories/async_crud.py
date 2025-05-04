# provides generic async CRUD operations (create, get_by_id, update, delete, list_all) to reduce boilerplate
## in concrete repositories.

from typing import Generic, TypeVar, Type, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class AsyncCrudRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    '''Base repository implementing common async CRUD operations.'''
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_by_id(self, id: str) -> ModelType:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()

    async def update(self, id: str, obj_in: UpdateSchemaType) -> ModelType:
        db_obj = await self.get_by_id(id)
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: str) -> None:
        db_obj = await self.get_by_id(id)
        await self.session.delete(db_obj)
        await self.session.commit()

    async def list_all(self) -> List[ModelType]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()    

        
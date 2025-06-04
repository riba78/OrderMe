# schema for user creation, update, and response including ID/timestamps.

from typing import Optional
from pydantic import BaseModel
from ..models.user import UserRole
from .base import IDModel, TimestampModel

class UserBase(BaseModel):
    role: UserRole
    is_active: Optional[bool]=True
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    pass 

class UserUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole]
    is_active: Optional[bool]
    class Config:
        from_attributes = True 

class UserResponse(IDModel, TimestampModel):
    role: UserRole 
    is_active: bool
    email: Optional[str] = None
    phone: Optional[str] = None


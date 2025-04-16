"""
User Schemas

This module contains Pydantic models for user-related data validation:
- UserCreate: For creating new users
- AdminManagerCreate: For creating admin/manager users
- CustomerCreate: For creating customer users
- UserProfileCreate: For creating user profiles
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from ..models import UserRole
from uuid import UUID

class UserBase(BaseModel):
    role: UserRole = UserRole.CUSTOMER

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID
    is_active: bool

    class Config:
        orm_mode = True

class AdminManagerBase(BaseModel):
    email: EmailStr
    verification_method: str = "email"
    tin_trunk_number: Optional[str] = None

class AdminManagerCreate(AdminManagerBase):
    user_id: Optional[UUID] = None
    password: str = Field(min_length=8)
    role: UserRole = UserRole.ADMIN

class AdminManagerUpdate(AdminManagerBase):
    password: Optional[str] = Field(min_length=8, default=None)

class AdminManagerResponse(AdminManagerBase):
    user_id: UUID

    class Config:
        orm_mode = True

class CustomerBase(BaseModel):
    phone_number: str

class CustomerCreate(CustomerBase):
    user_id: UUID
    created_by: UUID
    assigned_manager_id: UUID

class CustomerUpdate(CustomerBase):
    assigned_manager_id: Optional[UUID] = None

class CustomerResponse(CustomerBase):
    user_id: UUID
    created_by: UUID
    assigned_manager_id: UUID

    class Config:
        orm_mode = True

class UserProfileBase(BaseModel):
    first_name: str
    last_name: str
    business_name: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    user_id: UUID

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    user_id: UUID

    class Config:
        orm_mode = True 
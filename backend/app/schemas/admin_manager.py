from pydantic import BaseModel, EmailStr
from typing import Optional
from .base import IDModel, TimestampModel
from ..models.admin_manager import VerificationMethod

class AdminManagerBase(BaseModel):
    email: EmailStr
    verification_method: VerificationMethod = VerificationMethod.email # default to email when user created
    tin_trunk_number: Optional[str] = None
    class Config:
        from_attributes = True

class AdminManagerCreate(AdminManagerBase):
    password: str

class AdminManagerResponse(IDModel, TimestampModel, AdminManagerBase):
    pass 


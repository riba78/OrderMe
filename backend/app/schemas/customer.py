# schemas for customer creation and reponse including assigment info.

from pydantic import BaseModel, constr
from typing import Optional 
from typing_extensions import Annotated  # Use 'from typing import Annotated' if Python 3.9+
from .base import IDModel, TimestampModel 

class CustomerBase(BaseModel):
    phone: Annotated[str, constr(pattern=r"^\+?[0-9]{7,15}$")]
    class Config:
        from_attributes = True 

class CustomerCreate(CustomerBase):
    created_by: str
    assigned_manager_id: Optional[str] = None

class CustomerResponse(IDModel, TimestampModel, CustomerBase):
    created_by: str
    assigned_manager_id: Optional[str] = None 


    
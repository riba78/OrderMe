# base schemas with 'orm_mode' and tiemstamp fileds.

from pydantic import BaseModel
from datetime import datetime

class IDModel(BaseModel):
    id: str
    class Config:
        from_attributes = True

class TimestampModel(BaseModel):
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


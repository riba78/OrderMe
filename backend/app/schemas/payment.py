from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from uuid import UUID
from ..models.payment import PaymentStatus

class PaymentBase(BaseModel):
    amount: float = Field(gt=0)
    user_id: UUID
    order_id: UUID

class PaymentCreate(PaymentBase):
    payment_method_id: UUID

class PaymentUpdate(BaseModel):
    status: PaymentStatus

class PaymentResponse(PaymentBase):
    id: UUID
    status: PaymentStatus
    transaction_id: Optional[str] = None
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True

class PaymentMethodBase(BaseModel):
    type: str
    provider: str
    last_four: str = Field(min_length=4, max_length=4)
    expiry_date: date
    is_default: bool = False

class PaymentMethodCreate(PaymentMethodBase):
    user_id: UUID

class PaymentMethodUpdate(PaymentMethodBase):
    pass

class PaymentMethodResponse(PaymentMethodBase):
    id: UUID
    user_id: UUID
    created_at: date

    class Config:
        orm_mode = True

class PaymentInfoBase(BaseModel):
    billing_street: str
    billing_city: str
    billing_zip: str
    billing_country: str

class PaymentInfoCreate(PaymentInfoBase):
    user_id: UUID

class PaymentInfoUpdate(PaymentInfoBase):
    pass

class PaymentInfoResponse(PaymentInfoBase):
    id: UUID
    user_id: UUID
    created_at: date

    class Config:
        orm_mode = True 
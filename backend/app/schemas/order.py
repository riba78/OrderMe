"""
Order Schemas

This module contains Pydantic models for order-related operations.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from ..models.enums import OrderStatus

class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: UUID
    order_id: UUID

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    user_id: UUID
    total_amount: float = Field(..., gt=0)
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None

class OrderResponse(OrderBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True 
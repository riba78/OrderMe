"""
Notification Model Module

This module defines the Notification model and related schemas including:
- Notification database model with fields for notification details
- Pydantic schemas for notification creation and updates
- Notification type and status management

It handles notification information, status tracking, and user preferences
through the defined models and schemas.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from .base import Base, TimestampMixin
from typing import Optional, TYPE_CHECKING
import enum

# Use forward references to avoid circular imports
if TYPE_CHECKING:
    from .order import Order

# SQLAlchemy Models
class NotificationType(enum.Enum):
    ORDER_STATUS = "order_status"
    PAYMENT = "payment"
    SYSTEM = "system"

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=True)
    type = Column(String(50))  # Store enum value as string
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    order = relationship("Order", back_populates="notifications")

    def __init__(self, **kwargs):
        # Convert enum to string value before initialization
        if 'type' in kwargs and isinstance(kwargs['type'], NotificationType):
            kwargs['type'] = kwargs['type'].value
        super().__init__(**kwargs)

# Pydantic Schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType

class NotificationCreate(NotificationBase):
    user_id: str
    order_id: Optional[str] = None

class NotificationResponse(NotificationBase):
    id: str
    is_read: bool
    user_id: str
    order_id: Optional[str] = None

    class Config:
        orm_mode = True
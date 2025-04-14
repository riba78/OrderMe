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
import enum

# SQLAlchemy Models
class NotificationType(enum.Enum):
    ORDER_STATUS = "order_status"
    PAYMENT = "payment"
    SYSTEM = "system"

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(NotificationType))
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")

# Pydantic Schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    id: int
    is_read: bool
    user_id: int

    class Config:
        orm_mode = True
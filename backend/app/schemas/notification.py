"""
Notification Schemas

This module contains Pydantic models for notification-related operations.
"""

from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field
from app.models import NotificationType

class NotificationBase(BaseModel):
    """Base schema for notification data."""
    type: NotificationType
    title: str = Field(..., min_length=1)
    message: str
    is_read: bool = False
    related_order_id: Optional[UUID] = None

class NotificationCreate(NotificationBase):
    """Schema for creating a new notification."""
    user_id: UUID

class Notification(NotificationBase):
    """Schema for notification response."""
    id: UUID
    user_id: UUID
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True 
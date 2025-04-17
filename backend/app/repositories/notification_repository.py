"""
Notification Repository Module

This module defines the NotificationRepository class that handles database operations
for the Notification model including:
- Notification-specific queries
- Notification status management
- User notification retrieval
- Order-related notification queries

It extends the BaseRepository and provides specialized methods
for notification-related database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.notification import Notification
from ..models.enums import NotificationType
from .base_repository import BaseRepository

class NotificationRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(Notification, session)

    def get_by_user_id(self, user_id: str) -> List[Notification]:
        """Get all notifications for a specific user."""
        return self.session.query(Notification).filter(Notification.user_id == user_id).all()

    def get_unread_notifications(self, user_id: str) -> List[Notification]:
        """Get all unread notifications for a user."""
        return self.session.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).all()

    def get_by_type(self, type: NotificationType, user_id: str = None) -> List[Notification]:
        """Get notifications by type with optional user filtering."""
        query = self.session.query(Notification).filter(Notification._type == type.value)
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        return query.all()

    def get_by_order_id(self, order_id: str) -> List[Notification]:
        """Get all notifications related to a specific order."""
        return self.session.query(Notification).filter(Notification.order_id == order_id).all()
    
    def mark_as_read(self, notification_id: str) -> Optional[Notification]:
        """Mark a notification as read."""
        return self.update(notification_id, {"is_read": True})
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read and return the count of updated notifications."""
        result = self.session.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        self.session.commit()
        return result 
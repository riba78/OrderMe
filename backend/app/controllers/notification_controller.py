"""
Notification Controller Module

This module handles all notification-related endpoints including:
- Notification creation
- Notification retrieval
- Notification status updates
- Notification preferences

It provides functionality for managing user notifications and
includes features for notification status tracking and preferences.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.models.models import Notification, NotificationType
from app.database import get_db
from app.controllers.auth_controller import get_current_user

router = APIRouter()

# Pydantic models
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

# Endpoints
@router.get("/test")
async def test_notification():
    """Test endpoint to verify the notification controller is working"""
    return {"message": "Notification controller is working"}

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    """Create a new notification"""
    db_notification = Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.get("/user/{user_id}", response_model=List[NotificationResponse])
async def get_user_notifications(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all notifications for a specific user"""
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user's notifications"
        )
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).offset(skip).limit(limit).all()
    return notifications

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify other user's notifications"
        )
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other user's notifications"
        )
    
    db.delete(notification)
    db.commit()
    return None 
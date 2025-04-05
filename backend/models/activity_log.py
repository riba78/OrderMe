"""
Activity Log Model Module

This module defines the ActivityLog model for tracking user actions and system events.
The model stores detailed information about user activities, including:
- User who performed the action
- Type of action
- Entity affected
- Additional metadata
- IP address and user agent for security tracking
"""

from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db

class ActivityLog(db.Model):
    """
    Model for tracking user activities and system events.
    """
    __tablename__ = 'activity_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'login', 'create', 'update'
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., 'user', 'customer'
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 compatible
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship back to user
    user = relationship('User', back_populates='activity_logs')

    def to_dict(self):
        """Convert activity log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'metadata': self.metadata,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 
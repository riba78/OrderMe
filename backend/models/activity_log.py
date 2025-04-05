"""
Activity Log Model Module

This module defines the ActivityLog model for tracking user actions and system events.
The model stores detailed information about user activities, including:
- User who performed the action
- Type of action
- Entity affected
- Additional metadata
- IP address and user agent for security tracking

The table is partitioned by RANGE on created_at for efficient data management.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, JSON, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class ActivityLog(Base):
    """
    Activity log model for tracking user actions.
    Records all significant actions performed by users in the system.
    Table is partitioned by RANGE on created_at for efficient data management.
    """
    __tablename__ = 'activity_logs'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_row_format': 'DYNAMIC',
        'info': {'is_partitioned': True}  # Marker for migration script
    }

    # Primary key must include the partitioning key (created_at)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        primary_key=True,  # Part of primary key for partitioning
        index=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship('User', back_populates='activity_logs')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        """Convert activity log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'meta_data': self.meta_data,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': {
                'id': self.user.id,
                'email': self.user.email
            } if self.user else None
        }

    @classmethod
    def log_activity(cls, user_id: int, action_type: str, entity_type: str, entity_id: int,
                    description: str = None, metadata: dict = None, ip_address: str = None,
                    user_agent: str = None) -> 'ActivityLog':
        """
        Create a new activity log entry.
        
        Args:
            user_id: ID of the user performing the action
            action_type: Type of action performed (e.g., 'login', 'create', 'update')
            entity_type: Type of entity affected (e.g., 'user', 'customer', 'order')
            entity_id: ID of the affected entity
            description: Optional description of the action
            metadata: Optional additional data about the action
            ip_address: Optional IP address of the user
            user_agent: Optional user agent string
        
        Returns:
            ActivityLog: The created activity log entry
        """
        return cls(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            meta_data=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        ) 
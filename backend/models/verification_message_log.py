"""
Verification Message Log Model Module

This module defines the VerificationMessageLog model for tracking verification attempts.
The model stores information about verification messages sent to users, including:
- User who received the message
- Verification method used
- Message type and content
- Provider information
- Status tracking

The table is partitioned by RANGE on created_at for efficient data management.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, JSON, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class VerificationMessageLog(Base):
    """
    Log model for tracking verification message delivery attempts.
    Records all verification messages sent through various providers.
    Table is partitioned by RANGE on created_at for efficient data management.
    """
    __tablename__ = 'verification_messages_log'
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
    method_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'email', 'phone', 'whatsapp'
    message_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'verification', 'reset', 'change'
    identifier: Mapped[str] = mapped_column(String(120), nullable=False)  # email or phone number
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # 'sent', 'delivered', 'failed'
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 'smtp', 'twilio', 'whatsapp'
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    user = relationship('User', backref='verification_messages')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        """Convert verification message log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'method_type': self.method_type,
            'message_type': self.message_type,
            'identifier': self.identifier,
            'status': self.status,
            'provider': self.provider,
            'provider_message_id': self.provider_message_id,
            'error_message': self.error_message,
            'meta_data': self.meta_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': {
                'id': self.user.id,
                'email': self.user.email
            } if self.user else None
        }

    @classmethod
    def log_message(cls, user_id: int, method_type: str, message_type: str, identifier: str,
                   status: str, provider: str, provider_message_id: str = None,
                   error_message: str = None, metadata: dict = None) -> 'VerificationMessageLog':
        """
        Create a new verification message log entry.
        
        Args:
            user_id: ID of the user receiving the message
            method_type: Type of verification method ('email', 'phone', 'whatsapp')
            message_type: Type of message ('verification', 'reset', 'change')
            identifier: Recipient identifier (email or phone number)
            status: Message status ('sent', 'delivered', 'failed')
            provider: Service provider used ('smtp', 'twilio', 'whatsapp')
            provider_message_id: Optional provider's message ID
            error_message: Optional error message if status is 'failed'
            metadata: Optional additional data about the message
        
        Returns:
            VerificationMessageLog: The created log entry
        """
        return cls(
            user_id=user_id,
            method_type=method_type,
            message_type=message_type,
            identifier=identifier,
            status=status,
            provider=provider,
            provider_message_id=provider_message_id,
            error_message=error_message,
            meta_data=metadata
        ) 
"""
Verification Message Log Model Module

This module defines the VerificationMessageLog model for tracking verification attempts.
The model stores information about verification messages sent to users, including:
- User who received the message
- Verification method used
- Message type and content
- Provider information
- Status tracking
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db
from models.user import VerificationMethod

class VerificationMessageLog(db.Model):
    """
    Model for tracking verification messages sent to users.
    """
    __tablename__ = 'verification_messages_log'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    method_type: Mapped[VerificationMethod] = mapped_column(String(20), nullable=False)  # Using string for flexibility
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'verification', 'password_reset'
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)  # email, phone number, etc.
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., 'sent', 'delivered', 'failed'
    provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., 'sendgrid', 'twilio'
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship back to user
    user = relationship('User')

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
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 
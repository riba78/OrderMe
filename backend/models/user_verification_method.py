"""
User Verification Method Model Module

This module defines the UserVerificationMethod model for managing user verification methods.
The model stores information about different verification methods (email, phone, whatsapp)
associated with users and tracks their verification status.
"""

from datetime import datetime, timedelta
import secrets
from typing import Optional
from sqlalchemy import Integer, BigInteger, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .user import VerificationMethod

class UserVerificationMethod(Base):
    """
    Model for tracking user verification methods and their status.
    Each user can have multiple verification methods (email, phone, whatsapp).
    """
    __tablename__ = 'user_verification_methods'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_row_format': 'DYNAMIC'
    }

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    method_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'email', 'phone', 'whatsapp'
    identifier: Mapped[str] = mapped_column(String(120), nullable=False)  # email or phone number
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_verification_attempt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verification_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', backref='verification_methods')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        """Convert verification method to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'method_type': self.method_type,
            'identifier': self.identifier,
            'is_verified': self.is_verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'last_verification_attempt': self.last_verification_attempt.isoformat() if self.last_verification_attempt else None,
            'verification_attempts': self.verification_attempts,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def generate_code(self) -> str:
        """Generate a new verification code and token."""
        # Generate a secure random token
        self.verification_token = secrets.token_urlsafe(32)
        # Set expiration time (24 hours for email, 15 minutes for others)
        expiry_delta = timedelta(hours=24) if self.method_type == VerificationMethod.EMAIL else timedelta(minutes=15)
        self.token_expires = datetime.utcnow() + expiry_delta
        # Generate a 6-digit code for SMS/WhatsApp or longer token for email
        code = ''.join(secrets.choice('0123456789') for _ in range(6))
        return code

    def verify_code(self, code: str) -> bool:
        """
        Verify the provided code against the stored verification token.
        
        Args:
            code: The verification code to check
            
        Returns:
            bool: True if verification successful, False otherwise
        """
        self.verification_attempts += 1
        self.last_verification_attempt = datetime.utcnow()
        
        # Check if token has expired
        if not self.token_expires or datetime.utcnow() > self.token_expires:
            return False
        
        # Verify the code
        if code == self.verification_token:
            self.mark_as_verified()
            return True
            
        return False

    def mark_as_verified(self):
        """Mark the verification method as verified."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verification_token = None
        self.token_expires = None 
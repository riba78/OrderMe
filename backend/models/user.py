"""
User Model Module

This module defines the User model and related models for the application:
1. UserRole: Enum defining possible user roles (ADMIN, USER, CUSTOMER)
2. User: Base SQLAlchemy model for user data management

User Model Features:
- Role-based access control
- User verification status
- Activity status tracking
- Audit fields (created_at, updated_at)
- User relationship tracking (created_by)
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import BigInteger, String, Boolean, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from werkzeug.security import generate_password_hash, check_password_hash

class UserRole(str, Enum):
    """Enum for user roles in the system."""
    ADMIN = 'ADMIN'
    USER = 'USER'
    CUSTOMER = 'CUSTOMER'

class VerificationMethod(str, Enum):
    """Enum for user verification methods."""
    EMAIL = 'email'
    PHONE = 'phone'
    WHATSAPP = 'whatsapp'

class User(Base):
    """
    User model for all user types.
    Contains common fields used across all roles.
    """
    __tablename__ = 'users'
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': 'role'
    }
    __table_args__ = (
        Index('idx_user_search', 'email', 'role', 'is_active'),
        Index('idx_uuid', 'uuid'),
        Index('idx_role', 'role'),
        Index('idx_verification', 'verification_token'),
        Index('idx_email_change', 'email_change_token'),
        Index('idx_created_at', 'created_at'),
        Index('idx_last_login', 'last_login_at'),
        Index('idx_created_by', 'created_by_id', 'created_as_role'),
        {'mysql_row_format': 'COMPRESSED'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    primary_verification_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verification_token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    email_change_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_change_new: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    email_change_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    login_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_as_role: Mapped[str] = mapped_column(String(20), nullable=False)

    # Relationships
    created_by = relationship(
        'User',
        remote_side=[id],
        backref='created_users',
        foreign_keys=[created_by_id],
        primaryjoin='User.created_by_id == User.id'
    )
    assigned_customers = relationship(
        'Customer',
        back_populates='assigned_to',
        foreign_keys='Customer.assigned_to_id',
        primaryjoin='User.id == Customer.assigned_to_id'
    )
    profile = relationship(
        'UserProfile',
        uselist=False,
        back_populates='user',
        cascade='all, delete-orphan'
    )
    activity_logs = relationship(
        'ActivityLog',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    def set_password(self, password: str):
        """Set password hash for the user."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_profile=False):
        """Convert user model to dictionary with proper string serialization."""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'email': self.email,
            'role': str(self.role),
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'primary_verification_method': self.primary_verification_method,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'login_count': self.login_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by_id': self.created_by_id,
            'created_as_role': str(self.created_as_role)
        }
        if include_profile and self.profile:
            data['profile'] = self.profile.to_dict()
        return data

    def update_last_login(self):
        """Update the last login timestamp and increment login count."""
        self.last_login_at = datetime.utcnow()
        self.login_count += 1

    def activate(self):
        """Activate the user."""
        self.is_active = True

    def deactivate(self):
        """Deactivate the user."""
        self.is_active = False

    def verify(self):
        """Mark the user as verified."""
        self.is_verified = True

    def change_role(self, new_role: UserRole):
        """Change the user's role."""
        self.role = new_role.value

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN.value

    @property
    def is_customer(self) -> bool:
        """Check if user has customer role."""
        return self.role == UserRole.CUSTOMER.value

class AdminUser(User):
    """Admin user type with full system access."""
    __mapper_args__ = {
        'polymorphic_identity': UserRole.ADMIN.value
    }

class RegularUser(User):
    """Regular user type with standard access."""
    __mapper_args__ = {
        'polymorphic_identity': UserRole.USER.value
    } 
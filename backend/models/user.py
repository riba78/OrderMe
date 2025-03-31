"""
User Model Module

This module defines the User model and related enums for the application:
1. UserRole: Enum defining possible user roles (ADMIN, USER, CUSTOMER)
2. User: SQLAlchemy model for user data management

User Model Features:
- Secure password hashing using Werkzeug
- Role-based access control
- User verification status
- Activity status tracking
- Audit fields (created_at, updated_at)
- User relationship tracking (created_by)

Key Methods:
- set_password: Securely hash and set user password
- check_password: Verify password against stored hash
- is_admin/is_customer: Role check properties
- create_admin: Factory method for admin user creation
- to_dict: Serialization for API responses

The User model is central to the application's authentication and
authorization system, managing all user-related data and operations.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    CUSTOMER = 'CUSTOMER'

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tin_trunk_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # For tracking who created this user (e.g., which admin)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    created_by = relationship('User', remote_side=[id], backref='created_users')

    def set_password(self, password: str) -> None:
        """Set the password hash using Werkzeug's generate_password_hash."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def update_tin_trunk_phone(self, phone: str) -> None:
        """Update the tin trunk phone number for AI ordering."""
        self.tin_trunk_phone = phone

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    @property
    def is_customer(self) -> bool:
        return self.role == UserRole.CUSTOMER
    
    @classmethod
    def create_admin(cls, email: str, name: str, password: str) -> "User":
        user = cls(
            email=email,
            name=name,
            role=UserRole.ADMIN,
            is_verified=True,
            is_active=True
        )
        user.set_password(password)
        return user
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'tin_trunk_phone': self.tin_trunk_phone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 
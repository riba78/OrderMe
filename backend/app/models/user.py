"""
User Model Module

This module defines the User model and related schemas including:
- User database model with fields for authentication and profile
- Pydantic schemas for user creation and updates
- User role and status management

It handles user authentication, profile management, and role-based
access control through the defined models and schemas.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from .base import Base, TimestampMixin
import enum
from datetime import datetime
from uuid import uuid4

# SQLAlchemy Models
class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    MANAGER = "manager"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    _role = Column("role", String(20), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    admin_manager = relationship("AdminManager", back_populates="user", uselist=False)
    customer = relationship("Customer", back_populates="user", foreign_keys="[Customer.user_id]", uselist=False)
    managed_customers = relationship("Customer", back_populates="assigned_manager", foreign_keys="[Customer.assigned_manager_id]")
    created_customers = relationship("Customer", back_populates="creator", foreign_keys="[Customer.created_by]")
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    addresses = relationship("Address", back_populates="user")
    payment_methods = relationship("PaymentMethod", back_populates="user")
    payment_infos = relationship("PaymentInfo", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    orders = relationship("Order", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

    @hybrid_property
    def role(self) -> UserRole:
        """Get the user's role as an enum value."""
        return UserRole(self._role) if self._role else None

    @role.setter
    def role(self, value: UserRole):
        """Set the user's role from an enum value."""
        self._role = value.value if value else None

    def __init__(self, **kwargs):
        if "role" in kwargs:
            role = kwargs.pop("role")
            kwargs["_role"] = role.value if isinstance(role, UserRole) else role
        super().__init__(**kwargs)

class AdminManager(Base, TimestampMixin):
    __tablename__ = "admin_manager"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    verification_method = Column(Enum("email", "phone", "WhatsApp", name="verification_method"), nullable=False)
    tin_trunk_number = Column(String(50))
    
    # Relationships
    user = relationship("User", back_populates="admin_manager")

class Customer(Base, TimestampMixin):
    __tablename__ = "customer"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    phone_number = Column(String(20), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    assigned_manager_id = Column(String(36), ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="customer", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])
    assigned_manager = relationship("User", foreign_keys=[assigned_manager_id])

class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profile"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    business_name = Column(String(255))
    
    # Relationships
    user = relationship("User", back_populates="profile")

class Address(Base, TimestampMixin):
    __tablename__ = "address"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    street = Column(String(255))
    city = Column(String(100))
    zip_code = Column(String(20))
    contact_phone = Column(String(20))
    country = Column(String(100))
    
    # Relationships
    user = relationship("User", back_populates="addresses")

# Pydantic Schemas
class UserBase(BaseModel):
    role: UserRole

class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole = UserRole.CUSTOMER

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    is_active: bool

    class Config:
        orm_mode = True
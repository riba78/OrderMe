"""
User Model Module

This module defines the User model and related models for the application:
1. UserRole: Enum defining possible user roles (ADMIN, USER, CUSTOMER)
2. User: Base SQLAlchemy model for user data management
3. UserProfile: Model for ADMIN and USER role-specific data
4. UserVerificationMethod: Model for user verification methods

User Model Features:
- Secure password hashing using Werkzeug
- Role-based access control
- User verification status
- Activity status tracking
- Audit fields (created_at, updated_at)
- User relationship tracking (created_by)
- Multiple verification methods support
- Verification status tracking

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
from typing import Optional, List
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
import uuid

class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    CUSTOMER = 'CUSTOMER'
    SYSTEM = 'SYSTEM'  # For system-created users

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"UserRole.{self.value}"

    @classmethod
    def coerce(cls, item):
        """Coerce a string or UserRole enum to a UserRole value."""
        if isinstance(item, str):
            return cls(item)
        elif isinstance(item, cls):
            return item
        elif item is None:
            return None
        raise ValueError(f'Invalid UserRole value: {item}')

class VerificationMethod(str, Enum):
    EMAIL = 'EMAIL'
    PHONE = 'PHONE'
    GOOGLE = 'GOOGLE'
    FACEBOOK = 'FACEBOOK'

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"VerificationMethod.{self.value}"

class User(db.Model):
    """
    Base User model for all user types.
    Contains common fields used across all roles.
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    primary_verification_method: Mapped[Optional[VerificationMethod]] = mapped_column(SQLEnum(VerificationMethod), nullable=True)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verification_token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    email_change_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_change_new: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    email_change_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # For tracking who created this user
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    created_as_role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False, default=UserRole.SYSTEM)
    created_by = relationship('User', remote_side=[id], backref='created_users', foreign_keys=[created_by_id])

    # Relationships
    profile = relationship('UserProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    verification_methods = relationship('UserVerificationMethod', back_populates='user', cascade='all, delete-orphan')
    assigned_customers = relationship('Customer', back_populates='assigned_to', foreign_keys='Customer.assigned_to_id')
    activity_logs = relationship('ActivityLog', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password: str) -> None:
        """Set the password hash using Werkzeug's generate_password_hash."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    @property
    def is_customer(self) -> bool:
        return self.role == UserRole.CUSTOMER
    
    @classmethod
    def create_admin(cls, email: str, password: str) -> "User":
        """Create an admin user with associated profile."""
        user = cls(
            uuid=str(uuid.uuid4()),
            email=email,
            role=UserRole.ADMIN,
            is_verified=True,
            is_active=True,
            created_as_role=UserRole.SYSTEM
        )
        user.set_password(password)
        user.profile = UserProfile()  # Create associated profile
        return user

    def to_dict(self):
        """Convert user model to dictionary with proper string serialization."""
        try:
            role_str = str(self.role.value) if self.role else None
            created_as_role_str = str(self.created_as_role.value) if self.created_as_role else None
            primary_verification_method_str = str(self.primary_verification_method.value) if self.primary_verification_method else None
            
            result = {
                'id': self.id,
                'uuid': self.uuid,
                'email': self.email,
                'role': role_str,
                'is_active': self.is_active,
                'is_verified': self.is_verified,
                'primary_verification_method': primary_verification_method_str,
                'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
                'login_count': self.login_count,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'created_as_role': created_as_role_str
            }

            # Add profile data if exists
            if self.profile:
                result.update(self.profile.to_dict())

            # Add verification methods
            if self.verification_methods:
                result['verification_methods'] = [method.to_dict() for method in self.verification_methods]

            # Add assigned customers count for admin/user roles
            if self.role in [UserRole.ADMIN, UserRole.USER]:
                result['assigned_customers_count'] = len(self.assigned_customers)
            
            return result
            
        except Exception as e:
            print(f"Error in to_dict for user {self.id}:")
            print(f"  - Error: {str(e)}")
            print(f"  - Role: {getattr(self, 'role', None)}")
            print(f"  - Role type: {type(getattr(self, 'role', None))}")
            raise

class UserProfile(db.Model):
    """
    Extended profile for ADMIN and USER roles.
    Contains fields specific to these roles.
    """
    __tablename__ = 'user_profiles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    profile_picture: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    search_vector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship back to user
    user = relationship('User', back_populates='profile')

    def to_dict(self):
        """Convert profile to dictionary."""
        return {
            'profile_picture': self.profile_picture,
            'bio': self.bio
        }

class UserVerificationMethod(db.Model):
    """
    Model for storing user verification methods.
    """
    __tablename__ = 'user_verification_methods'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    method_type: Mapped[VerificationMethod] = mapped_column(SQLEnum(VerificationMethod), nullable=False)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)  # email, phone number, etc.
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to user
    user = relationship('User', back_populates='verification_methods')

    def to_dict(self):
        """Convert verification method to dictionary."""
        return {
            'id': self.id,
            'method_type': str(self.method_type.value),
            'identifier': self.identifier,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 
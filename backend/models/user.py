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
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON, Index
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
    __mapper_args__ = {
        'polymorphic_identity': 'USER',
        'polymorphic_on': 'role',
        'with_polymorphic': '*'
    }
    __table_args__ = (
        Index('idx_user_search', 'email', 'role', 'is_active'),
        Index('idx_user_verification', 'is_verified', 'primary_verification_method'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.USER,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    primary_verification_method: Mapped[Optional[VerificationMethod]] = mapped_column(
        SQLEnum(VerificationMethod),
        nullable=True,
        index=True
    )
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    verification_token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    email_change_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    email_change_new: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    email_change_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # For tracking who created this user
    created_by_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )
    created_as_role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.SYSTEM
    )

    # Relationships
    created_by = relationship(
        'User',
        remote_side=[id],
        backref='created_users',
        foreign_keys=[created_by_id]
    )
    profile = relationship(
        'UserProfile',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan',
        lazy='joined'
    )
    verification_methods = relationship(
        'UserVerificationMethod',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='select'
    )
    assigned_customers = relationship(
        'Customer',
        back_populates='assigned_to',
        foreign_keys='Customer.assigned_to_id',
        lazy='select'
    )
    activity_logs = relationship(
        'ActivityLog',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='select'
    )

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
        return {
            'id': self.id,
            'uuid': self.uuid,
            'email': self.email,
            'role': str(self.role),
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'primary_verification_method': str(self.primary_verification_method) if self.primary_verification_method else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'login_count': self.login_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by_id': self.created_by_id,
            'created_as_role': str(self.created_as_role),
            'profile': self.profile.to_dict() if self.profile else None,
            'verification_methods': [vm.to_dict() for vm in self.verification_methods] if self.verification_methods else []
        }

class UserProfile(db.Model):
    """Profile information for ADMIN and USER roles."""
    __tablename__ = 'user_profiles'
    __table_args__ = (
        Index('idx_profile_search', 'first_name', 'last_name', 'business_name'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    business_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    street: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tin_trunk_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='profile')

    def to_dict(self):
        """Convert profile to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'business_name': self.business_name,
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'phone_number': self.phone_number,
            'tin_trunk_phone': self.tin_trunk_phone,
            'meta_data': self.meta_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def update_address(self, street: str = None, city: str = None, state: str = None, 
                      zip_code: str = None, country: str = None) -> None:
        """Update address fields."""
        if street is not None:
            self.street = street
        if city is not None:
            self.city = city
        if state is not None:
            self.state = state
        if zip_code is not None:
            self.zip_code = zip_code
        if country is not None:
            self.country = country

    def update_contact(self, phone_number: str = None, tin_trunk_phone: str = None) -> None:
        """Update contact information."""
        if phone_number is not None:
            self.phone_number = phone_number
        if tin_trunk_phone is not None:
            self.tin_trunk_phone = tin_trunk_phone

    def update_business(self, business_name: str = None) -> None:
        """Update business information."""
        if business_name is not None:
            self.business_name = business_name

class UserVerificationMethod(db.Model):
    """
    Model for tracking user verification methods and their status.
    Each user can have multiple verification methods (email, phone, etc.).
    """
    __tablename__ = 'user_verification_methods'
    __table_args__ = (
        Index('idx_verification_method', 'user_id', 'method_type', 'is_verified'),
        Index('idx_verification_token', 'verification_token', 'token_expires'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    method_type: Mapped[VerificationMethod] = mapped_column(SQLEnum(VerificationMethod), nullable=False)
    identifier: Mapped[str] = mapped_column(String(120), nullable=False)  # email or phone number
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_verification_attempt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verification_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    verification_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='verification_methods')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        """Convert verification method to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'method_type': str(self.method_type),
            'identifier': self.identifier,
            'is_verified': self.is_verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'last_verification_attempt': self.last_verification_attempt.isoformat() if self.last_verification_attempt else None,
            'verification_attempts': self.verification_attempts,
            'verification_data': self.verification_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def record_verification_attempt(self) -> None:
        """Record a verification attempt."""
        self.verification_attempts += 1
        self.last_verification_attempt = datetime.utcnow()

    def mark_as_verified(self) -> None:
        """Mark the verification method as verified."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verification_token = None
        self.token_expires = None

    def set_verification_token(self, token: str, expires_in_hours: int = 24) -> None:
        """Set a new verification token with expiry."""
        self.verification_token = token
        self.token_expires = datetime.utcnow() + datetime.timedelta(hours=expires_in_hours) 
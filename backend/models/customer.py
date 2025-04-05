"""
Customer Model Module

This module defines the Customer model which inherits from the User model.
Customers are users with role='CUSTOMER' and have additional fields for
customer-specific information.

The model includes:
- Customer profile information
- Payment methods and billing info
- Assignment tracking
- Search optimization
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Column, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .user import User, UserRole

class PaymentMethod(Base):
    """Payment method information for customers."""
    __tablename__ = 'payment_methods'
    __table_args__ = (
        Index('idx_customer_default', 'customer_id', 'is_default'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    last_four: Mapped[str] = mapped_column(String(4), nullable=False)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class PaymentInfo(Base):
    """Billing information for customers."""
    __tablename__ = 'payment_info'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    billing_address: Mapped[str] = mapped_column(Text, nullable=False)
    billing_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    billing_state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    billing_zip: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    billing_country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class Customer(User):
    """
    Customer model inheriting from User.
    Contains customer-specific fields and relationships.
    """
    __tablename__ = 'customers'
    __mapper_args__ = {
        'polymorphic_identity': UserRole.CUSTOMER,
    }
    __table_args__ = (
        Index('idx_customer_search', 'business_name', 'nickname', 'first_name', 'last_name'),
        Index('idx_customer_assignment', 'assigned_to_id', 'last_activity_at'),
    )

    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    nickname: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    business_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    street: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    shipping_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    search_vector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Assignment tracking
    assigned_to_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    last_assigned_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    assigned_to = relationship(
        'User',
        foreign_keys=[assigned_to_id],
        back_populates='assigned_customers'
    )
    last_assigned_by = relationship(
        'User',
        foreign_keys=[last_assigned_by_id]
    )
    payment_methods: Mapped[List["PaymentMethod"]] = relationship(
        lazy="select",
        backref="customer",
        cascade="all, delete-orphan"
    )
    payment_info: Mapped[Optional["PaymentInfo"]] = relationship(
        uselist=False,
        backref="customer",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Convert customer to dictionary."""
        base_dict = super().to_dict()
        customer_dict = {
            'nickname': self.nickname,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'business_name': self.business_name,
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'phone_number': self.phone_number,
            'meta_data': self.meta_data,
            'shipping_address': self.shipping_address,
            'assigned_to_id': self.assigned_to_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'last_assigned_by_id': self.last_assigned_by_id,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
            'payment_methods': [pm.to_dict() for pm in self.payment_methods] if self.payment_methods else [],
            'payment_info': self.payment_info.to_dict() if self.payment_info else None
        }
        base_dict.update(customer_dict)
        return base_dict
    
    def add_payment_method(self, payment_method: PaymentMethod) -> None:
        """Add a new payment method."""
        if payment_method.is_default:
            # Set all other payment methods to non-default
            for pm in self.payment_methods:
                pm.is_default = False
        self.payment_methods.append(payment_method)
    
    def get_payment_method(self, payment_id: int) -> Optional[PaymentMethod]:
        """Get a specific payment method by ID."""
        return next((pm for pm in self.payment_methods if pm.id == payment_id), None)
    
    def set_default_payment_method(self, payment_id: int) -> bool:
        """Set a payment method as default."""
        payment_method = self.get_payment_method(payment_id)
        if payment_method:
            for pm in self.payment_methods:
                pm.is_default = (pm.id == payment_id)
            return True
        return False
    
    def update_shipping_address(self, address: str) -> None:
        """Update the shipping address."""
        self.shipping_address = address
        
    def update_phone_number(self, phone: str) -> None:
        """Update the phone number."""
        self.phone_number = phone

    def update_billing_address(self, address: str, city: str = None, state: str = None,
                             zip_code: str = None, country: str = None) -> None:
        """Update the customer's billing address."""
        if not self.payment_info:
            self.payment_info = PaymentInfo(
                billing_address=address,
                billing_city=city,
                billing_state=state,
                billing_zip=zip_code,
                billing_country=country
            )
        else:
            self.payment_info.billing_address = address
            if city is not None:
                self.payment_info.billing_city = city
            if state is not None:
                self.payment_info.billing_state = state
            if zip_code is not None:
                self.payment_info.billing_zip = zip_code
            if country is not None:
                self.payment_info.billing_country = country

    def add_loyalty_points(self, points: int) -> None:
        """Add loyalty points to the customer's account."""
        # Loyalty points logic would be implemented here
        pass

    def use_loyalty_points(self, points: int) -> bool:
        """Use loyalty points for a purchase."""
        # Loyalty points logic would be implemented here
        return False

    def update_order_stats(self, order_amount: float) -> None:
        """Update customer's order statistics."""
        # Order statistics logic would be implemented here
        pass

    def assign_to_user(self, user_id: int, assigned_by_id: int) -> None:
        """Assign the customer to a user."""
        self.assigned_to_id = user_id
        self.last_assigned_by_id = assigned_by_id
        self.assigned_at = datetime.utcnow()
        self.last_activity_at = datetime.utcnow()

    def remove_assignment(self) -> None:
        """Remove the customer's assignment."""
        self.assigned_to_id = None
        self.last_assigned_by_id = None
        self.assigned_at = None 
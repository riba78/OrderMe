"""
Payment Models Module

This module defines the payment-related models:
- Payment: Handles payment transactions
- PaymentMethod: Stores payment methods (credit cards, etc.)
- PaymentInfo: Stores billing information

The models follow SOLID principles and maintain proper relationships
with User and Order models.
"""

from sqlalchemy import Column, String, Float, ForeignKey, Boolean, Enum, Date, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, List, TYPE_CHECKING
from datetime import date
from .base import Base, TimestampMixin
from .enums import PaymentStatus
from .user import User

# Use forward references to avoid circular imports
if TYPE_CHECKING:
    from .models import Order

class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    # Foreign key fields
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), unique=True)
    payment_method_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("payment_methods.id"))
    # Data fields
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")
    order: Mapped["Order"] = relationship("Order", back_populates="payments")
    payment_method: Mapped[Optional["PaymentMethod"]] = relationship("PaymentMethod", back_populates="payments")

class PaymentMethod(Base, TimestampMixin):
    __tablename__ = "payment_methods"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    # Foreign key fields
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    # Data fields
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(50))
    last_four: Mapped[Optional[str]] = mapped_column(String(4))
    expiry_date: Mapped[Optional[Date]] = mapped_column(Date)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payment_methods")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="payment_method")
    payment_info: Mapped[Optional["PaymentInfo"]] = relationship("PaymentInfo", back_populates="payment_method", uselist=False)

class PaymentInfo(Base, TimestampMixin):
    __tablename__ = "payment_info"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    # Foreign key fields
    payment_method_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("payment_methods.id"), unique=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    # Data fields
    billing_street: Mapped[Optional[str]] = mapped_column(String(255))
    billing_city: Mapped[Optional[str]] = mapped_column(String(100))
    billing_zip: Mapped[Optional[str]] = mapped_column(String(20))
    billing_country: Mapped[Optional[str]] = mapped_column(String(100))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    payment_method: Mapped["PaymentMethod"] = relationship("PaymentMethod", back_populates="payment_info")
    user: Mapped["User"] = relationship("User", back_populates="payment_infos")
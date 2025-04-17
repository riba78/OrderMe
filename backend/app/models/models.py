"""
Models Module

This module defines the core database models for the application using SQLAlchemy ORM.
It includes the following models:

- Category: Manages product categorization
- Product: Stores product information and inventory
- Notification: Manages user notifications and alerts

Each model follows SOLID principles:
- Single Responsibility: Each model handles one specific domain entity
- Open/Closed: Models are extendable through relationships
- Liskov Substitution: All models inherit from Base and TimestampMixin
- Interface Segregation: Models only include relevant fields and relationships
- Dependency Inversion: Models depend on abstractions (Base, enums) not concrete implementations

The models use SQLAlchemy relationships to maintain referential integrity
and provide easy navigation between related entities.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum, Text, DateTime, Date, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Union, List, Optional, TYPE_CHECKING
from .base import Base, TimestampMixin
from .enums import UserRole, OrderStatus, NotificationType
from .user import User, AdminManager, Customer, UserProfile
from uuid import uuid4
from datetime import datetime

# Use forward references to avoid circular imports
if TYPE_CHECKING:
    from .payment import Payment, PaymentMethod, PaymentInfo
    from .order import Order, OrderItem

class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")

class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    # Foreign key fields
    category_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("categories.id"))
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    min_stock_level: Mapped[int] = mapped_column(Integer, nullable=False)
    max_stock_level: Mapped[int] = mapped_column(Integer, nullable=False)
    qty_in_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    last_restock_date: Mapped[Optional[datetime]] = mapped_column(Date)
    
    # Relationships
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")
    creator: Mapped["User"] = relationship("User")

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    # Foreign key fields
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    order_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("orders.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(50))  # Store enum value as string
    title: Mapped[str] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="notifications")

    def __init__(self, **kwargs):
        # Convert enum to string value before initialization
        if 'type' in kwargs and isinstance(kwargs['type'], NotificationType):
            kwargs['type'] = kwargs['type'].value
        super().__init__(**kwargs) 
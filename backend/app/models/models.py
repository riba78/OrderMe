"""
Models Module

This module defines the core database models for the application using SQLAlchemy ORM.
It includes the following models:

- User: Base user model with role management
- AdminManager: Admin and manager specific fields
- Customer: Customer specific fields and relationships
- UserProfile: Additional user information
- Category: Manages product categorization
- Product: Stores product information and inventory
- Order: Manages customer orders and their lifecycle
- OrderItem: Represents individual items within an order
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

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum, Text, DateTime, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Union, List, Optional
from .base import Base, TimestampMixin
from .enums import UserRole, OrderStatus, NotificationType
from .payment import Payment, PaymentMethod, PaymentInfo
from .user import User, AdminManager, Customer, UserProfile
from uuid import uuid4
from datetime import datetime

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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("categories.id"))
    min_stock_level: Mapped[int] = mapped_column(Integer, nullable=False)
    max_stock_level: Mapped[int] = mapped_column(Integer, nullable=False)
    qty_in_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    last_restock_date: Mapped[Optional[datetime]] = mapped_column(Date)
    
    # Relationships
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")
    creator: Mapped["User"] = relationship("User")

class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50))  # Store enum value as string
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    shipping_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    billing_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="order")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="order")

    def __init__(self, **kwargs):
        # Convert enum to string value before initialization
        if 'status' in kwargs and isinstance(kwargs['status'], OrderStatus):
            kwargs['status'] = kwargs['status'].value
        super().__init__(**kwargs)

    @property
    def order_status(self) -> OrderStatus:
        return OrderStatus(self.status)

    @order_status.setter
    def order_status(self, value: OrderStatus):
        self.status = value.value

class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(50))  # Store enum value as string
    title: Mapped[str] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    related_order_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("orders.id"), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="notifications")

    def __init__(self, **kwargs):
        # Convert enum to string value before initialization
        if 'type' in kwargs and isinstance(kwargs['type'], NotificationType):
            kwargs['type'] = kwargs['type'].value
        super().__init__(**kwargs) 
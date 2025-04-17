"""
Order Models Module

This module defines Order-related database models using SQLAlchemy ORM:
- Order: Manages customer orders and their lifecycle
- OrderItem: Represents individual items within an order

Each model follows SOLID principles:
- Single Responsibility: Each model handles one specific aspect of orders
- Open/Closed: Models are extendable through relationships
- Liskov Substitution: All models inherit from Base and TimestampMixin
- Interface Segregation: Models only include relevant fields and relationships
- Dependency Inversion: Models depend on abstractions (Base, enums) not concrete implementations
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional, TYPE_CHECKING
from .base import Base, TimestampMixin
from .enums import OrderStatus
from uuid import uuid4

# Use forward references to avoid circular imports
if TYPE_CHECKING:
    from .user import User
    from .notification import Notification
    from .payment import Payment

class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    # Foreign key fields
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50))  # Store enum value as string
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
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
    # Foreign key fields
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items") 
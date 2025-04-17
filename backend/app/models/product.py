"""
Product Model Module

This module defines the Product and Category models for business logic handling:
- Product database model with fields for product details
- Category database model for product categorization
- Domain behavior for product stock management
- Business validation rules
- Event notification for important state changes
"""

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Text, Integer, Date, Numeric
from sqlalchemy.orm import relationship
from typing import Optional, List, Dict, Any
from datetime import date
from .base import Base, TimestampMixin
from ..utils.events import DomainEvent


class LowStockEvent(DomainEvent):
    """Event triggered when product stock falls below minimum level."""
    
    def __init__(self, product_id: str, current_stock: int, min_stock: int):
        self.product_id = product_id
        self.current_stock = current_stock
        self.min_stock = min_stock
        
    def __str__(self) -> str:
        return f"Product {self.product_id} has low stock: {self.current_stock}/{self.min_stock}"


class OutOfStockEvent(DomainEvent):
    """Event triggered when product goes out of stock."""
    
    def __init__(self, product_id: str):
        self.product_id = product_id
        
    def __str__(self) -> str:
        return f"Product {self.product_id} is out of stock"


# SQLAlchemy Models
class Category(Base, TimestampMixin):
    __tablename__ = "categories"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True)  # UUID
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    
    def validate(self) -> List[str]:
        """Validate category data."""
        errors = []
        if not self.name or len(self.name) < 1:
            errors.append("Category name is required")
        elif len(self.name) > 100:
            errors.append("Category name must be 100 characters or less")
        return errors


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True)  # UUID
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)
    category_id = Column(String(36), ForeignKey("categories.id"))
    min_stock_level = Column(Integer, nullable=False)
    max_stock_level = Column(Integer, nullable=False)
    qty_in_stock = Column(Integer, default=0)
    last_restock_date = Column(Date)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    order_items = relationship("app.models.order.OrderItem", back_populates="product")
    creator = relationship("app.models.user.User")
    
    @property
    def is_in_stock(self) -> bool:
        """Check if product is in stock."""
        return self.qty_in_stock > 0
    
    @property
    def needs_restock(self) -> bool:
        """Check if product needs to be restocked."""
        return self.qty_in_stock <= self.min_stock_level
    
    def update_stock(self, quantity_change: int) -> List[DomainEvent]:
        """
        Update product stock and generate events if needed.
        
        Returns:
            List of domain events triggered by this stock change.
        """
        events = []
        old_qty = self.qty_in_stock
        self.qty_in_stock += quantity_change
        
        # Generate events based on stock changes
        if old_qty > self.min_stock_level and self.qty_in_stock <= self.min_stock_level:
            events.append(LowStockEvent(self.id, self.qty_in_stock, self.min_stock_level))
            
        if old_qty > 0 and self.qty_in_stock <= 0:
            events.append(OutOfStockEvent(self.id))
            
        return events
    
    def restock(self, quantity: int) -> None:
        """Restock the product and update last restock date."""
        if quantity <= 0:
            raise ValueError("Restock quantity must be positive")
            
        self.update_stock(quantity)
        self.last_restock_date = date.today()
    
    def validate(self) -> List[str]:
        """Validate product data against business rules."""
        errors = []
        
        if not self.product_name or len(self.product_name) < 1:
            errors.append("Product name is required")
        elif len(self.product_name) > 255:
            errors.append("Product name must be 255 characters or less")
            
        if self.price is None or self.price <= 0:
            errors.append("Price must be greater than zero")
            
        if self.min_stock_level < 0:
            errors.append("Minimum stock level cannot be negative")
            
        if self.max_stock_level <= self.min_stock_level:
            errors.append("Maximum stock level must be greater than minimum stock level")
            
        if self.qty_in_stock < 0:
            errors.append("Quantity in stock cannot be negative")
            
        return errors
"""
Product Model Module

This module defines the Product and Category models and related schemas including:
- Product database model with fields for product details
- Category database model for product categorization
- Pydantic schemas for product and category management

It handles product information, categorization, and availability
management through the defined models and schemas.
"""

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Text, Integer, Date
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional
from .base import Base, TimestampMixin

# SQLAlchemy Models
class Category(Base, TimestampMixin):
    __tablename__ = "categories"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True)  # UUID
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Relationships
    products = relationship("app.models.product.Product", back_populates="category")

class Product(Base, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True)  # UUID
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String(255))
    is_available = Column(Boolean, default=True)
    category_id = Column(String(36), ForeignKey("categories.id"))
    min_stock_level = Column(Integer, nullable=False)
    max_stock_level = Column(Integer, nullable=False)
    qty_in_stock = Column(Integer, default=0)
    last_restock_date = Column(Date)
    
    # Relationships
    category = relationship("app.models.product.Category", back_populates="products")
    order_items = relationship("app.models.models.OrderItem", back_populates="product")
    creator = relationship("app.models.user.User")

# Pydantic Schemas
class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: str

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(gt=0)
    image_url: Optional[str] = None
    category_id: str
    is_available: bool = True
    min_stock_level: int = Field(gt=0)
    max_stock_level: int = Field(gt=0)
    last_restock_date: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: str
    category: CategoryResponse

    class Config:
        orm_mode = True
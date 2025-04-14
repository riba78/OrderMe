"""
Product Schemas

This module contains Pydantic models for product-related data validation:
- CategoryBase: Base schema for category data
- CategoryCreate: For creating new categories
- CategoryResponse: For returning category data
- ProductBase: Base schema for product data
- ProductCreate: For creating new products
- ProductResponse: For returning product data
"""

from pydantic import BaseModel, Field
from typing import Optional
from ..models import Category

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
    qty_in_stock: int = Field(ge=0)
    created_by: str

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: str
    category: CategoryResponse

    class Config:
        orm_mode = True 
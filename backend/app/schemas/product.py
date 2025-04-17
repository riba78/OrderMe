"""
Product Schemas

This module contains Pydantic models for product-related data validation:
- CategoryBase: Base schema for category data
- CategoryCreate: For creating new categories
- CategoryUpdate: For updating existing categories
- CategoryResponse: For returning category data
- ProductBase: Base schema for product data
- ProductCreate: For creating new products
- ProductUpdate: For updating existing products
- ProductResponse: For returning product data
- StockUpdateRequest: For updating product stock levels
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List
from datetime import date
from decimal import Decimal
from ..models import Category

class CategoryBase(BaseModel):
    """Base schema for category data."""
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    """Schema for creating new categories."""
    pass

class CategoryUpdate(CategoryBase):
    """Schema for updating existing categories."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class CategoryResponse(CategoryBase):
    """Schema for returning category data."""
    id: str

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    """Base schema for product data."""
    product_name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(gt=0)
    image_url: Optional[str] = None
    category_id: str
    is_available: bool = True
    min_stock_level: int = Field(gt=0)
    max_stock_level: int = Field(gt=0)
    qty_in_stock: int = Field(ge=0)
    last_restock_date: Optional[date] = None
    created_by: str
    
    @validator('max_stock_level')
    def max_stock_must_be_greater_than_min(cls, v, values):
        """Validate that max stock level is greater than min stock level."""
        if 'min_stock_level' in values and v <= values['min_stock_level']:
            raise ValueError('Maximum stock level must be greater than minimum stock level')
        return v

class ProductCreate(ProductBase):
    """Schema for creating new products."""
    pass

class ProductUpdate(BaseModel):
    """Schema for updating existing products."""
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    image_url: Optional[str] = None
    category_id: Optional[str] = None
    is_available: Optional[bool] = None
    min_stock_level: Optional[int] = Field(None, gt=0)
    max_stock_level: Optional[int] = Field(None, gt=0)
    last_restock_date: Optional[date] = None
    qty_in_stock: Optional[int] = Field(None, ge=0)
    created_by: Optional[str] = None
    
    @root_validator
    def validate_stock_levels(cls, values):
        """Validate stock level consistency when both are provided."""
        min_stock = values.get('min_stock_level')
        max_stock = values.get('max_stock_level')
        
        if min_stock is not None and max_stock is not None and max_stock <= min_stock:
            raise ValueError('Maximum stock level must be greater than minimum stock level')
        return values

class ProductResponse(BaseModel):
    """Schema for returning product data."""
    id: str
    product_name: str
    description: Optional[str]
    price: Decimal
    image_url: Optional[str]
    category_id: str
    is_available: bool
    min_stock_level: int
    max_stock_level: int
    qty_in_stock: int
    last_restock_date: Optional[date]
    created_by: str
    category: CategoryResponse
    is_in_stock: bool
    needs_restock: bool

    class Config:
        orm_mode = True

class StockUpdateRequest(BaseModel):
    """Schema for updating product stock levels."""
    quantity_change: int = Field(description="Positive for stock increase, negative for decrease")
    
    @validator('quantity_change')
    def validate_quantity_change(cls, v):
        """Validate that quantity change is not zero."""
        if v == 0:
            raise ValueError('Quantity change cannot be zero')
        return v 
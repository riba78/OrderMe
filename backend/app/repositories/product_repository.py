"""
Product Repository Module

This module defines the ProductRepository and CategoryRepository classes that handle
database operations for the Product and Category models including:
- Product-specific queries
- Category-specific queries
- Product search functionality
- Product availability management
- Category-product relationships

It extends the BaseRepository and provides specialized methods
for product and category-related database operations.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from ..models.product import Product, Category
from .base_repository import BaseRepository
from .interfaces.product_repository import IProductRepository, ICategoryRepository


class ProductRepository(BaseRepository, IProductRepository):
    def __init__(self, session: Session):
        super().__init__(Product, session)

    def get_products_by_category(self, category_id: str) -> List[Product]:
        return self.session.query(Product).filter(Product.category_id == category_id).all()

    def get_available_products(self) -> List[Product]:
        return self.session.query(Product).filter(Product.is_available == True).all()

    def search_products(self, query: str) -> List[Product]:
        return self.session.query(Product).filter(
            Product.product_name.ilike(f"%{query}%") | 
            Product.description.ilike(f"%{query}%")
        ).all()


class CategoryRepository(BaseRepository, ICategoryRepository):
    def __init__(self, session: Session):
        super().__init__(Category, session)

    def get_category_with_products(self, category_id: str) -> Optional[Category]:
        return self.session.query(Category).filter(Category.id == category_id).first() 
"""
Product Service Module

This module defines the ProductService and CategoryService classes that handle
business logic for product and category-related operations including:
- Product creation and management
- Category creation and management
- Product availability management
- Product search functionality
- Category-product relationships

It provides a layer of business logic between the controllers
and repositories for product and category-related operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.product import Product, Category
from ..repositories.product_repository import ProductRepository, CategoryRepository
from ..schemas.product import ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate

class ProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository
    ):
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.db = product_repository.db

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.product_repository.get(product_id)

    def get_products(self) -> List[Product]:
        return self.product_repository.get_all()

    def get_products_by_category(self, category_id: int) -> List[Product]:
        return self.product_repository.get_products_by_category(category_id)

    def get_available_products(self) -> List[Product]:
        return self.product_repository.get_available_products()

    def search_products(self, query: str) -> List[Product]:
        return self.product_repository.search_products(query)

    def create_product(self, product_data: ProductCreate) -> Product:
        # Verify category exists
        category = self.category_repository.get(product_data.category_id)
        if not category:
            raise ValueError(f"Category with id {product_data.category_id} not found")

        product = Product(**product_data.dict())
        return self.product_repository.create(product)

    def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        product = self.product_repository.get(product_id)
        if product:
            for key, value in product_data.dict(exclude_unset=True).items():
                setattr(product, key, value)
            return self.product_repository.update(product)
        return None

    def toggle_product_availability(self, product_id: int) -> Optional[Product]:
        product = self.product_repository.get(product_id)
        if product:
            product.is_available = not product.is_available
            return self.product_repository.update(product)
        return None

class CategoryService:
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository
        self.db = category_repository.db

    def get_category(self, category_id: int) -> Optional[Category]:
        return self.category_repository.get(category_id)

    def get_categories(self) -> List[Category]:
        return self.category_repository.get_all()

    def create_category(self, category_data: CategoryCreate) -> Category:
        category = Category(**category_data.dict())
        return self.category_repository.create(category)

    def update_category(self, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
        category = self.category_repository.get(category_id)
        if category:
            for key, value in category_data.dict(exclude_unset=True).items():
                setattr(category, key, value)
            return self.category_repository.update(category)
        return None

    def delete_category(self, category_id: int) -> bool:
        # Check if category has products
        category = self.category_repository.get_category_with_products(category_id)
        if category and category.products:
            raise ValueError("Cannot delete category with associated products")
        return self.category_repository.delete(category_id) 
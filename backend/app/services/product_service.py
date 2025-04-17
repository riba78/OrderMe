"""
Product Service Module

This module defines the ProductService and CategoryService classes that handle
business logic for product and category-related operations including:
- Product creation and management
- Category creation and management
- Product availability management
- Product search functionality
- Category-product relationships
- Stock management with domain events

It provides a layer of business logic between the controllers
and repositories for product and category-related operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import date

from ..models.product import Product, Category, LowStockEvent, OutOfStockEvent
from ..repositories.interfaces.product_repository import IProductRepository, ICategoryRepository
from ..schemas.product import (
    ProductCreate, 
    ProductUpdate, 
    CategoryCreate, 
    CategoryUpdate,
    StockUpdateRequest
)
from ..utils.events import event_bus


class ProductService:
    def __init__(
        self,
        product_repository: IProductRepository,
        category_repository: ICategoryRepository
    ):
        self.product_repository = product_repository
        self.category_repository = category_repository

    def get_product(self, product_id: str) -> Optional[Product]:
        return self.product_repository.get_by_id(product_id)

    def get_products(self) -> List[Product]:
        return self.product_repository.get_all()

    def get_products_by_category(self, category_id: str) -> List[Product]:
        return self.product_repository.get_products_by_category(category_id)

    def get_available_products(self) -> List[Product]:
        return self.product_repository.get_available_products()

    def search_products(self, query: str) -> List[Product]:
        return self.product_repository.search_products(query)

    def create_product(self, product_data: ProductCreate) -> Product:
        # Verify category exists
        category = self.category_repository.get_by_id(product_data.category_id)
        if not category:
            raise ValueError(f"Category with id {product_data.category_id} not found")

        # Convert to dict and add UUID
        product_dict = product_data.dict()
        product_dict["id"] = str(uuid4())
        
        # Create the product
        product = self.product_repository.create(product_dict)
        
        # Check if initial stock triggers low stock event
        if product.needs_restock:
            event_bus.publish(LowStockEvent(
                product.id, 
                product.qty_in_stock, 
                product.min_stock_level
            ))
            
        return product

    def update_product(self, product_id: str, product_data: ProductUpdate) -> Optional[Product]:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            return None
            
        # Validate category if it's being updated
        if product_data.category_id and product_data.category_id != product.category_id:
            category = self.category_repository.get_by_id(product_data.category_id)
            if not category:
                raise ValueError(f"Category with id {product_data.category_id} not found")
        
        # Prepare update data
        update_data = product_data.dict(exclude_unset=True)
        
        # Validate stock level consistency
        if ('min_stock_level' in update_data or 'max_stock_level' in update_data):
            new_min = update_data.get('min_stock_level', product.min_stock_level)
            new_max = update_data.get('max_stock_level', product.max_stock_level)
            if new_max <= new_min:
                raise ValueError("Maximum stock level must be greater than minimum stock level")
        
        # Update and check for events
        updated_product = self.product_repository.update(product_id, update_data)
        
        # Check for stock-related events after update
        if updated_product.needs_restock and not product.needs_restock:
            event_bus.publish(LowStockEvent(
                updated_product.id, 
                updated_product.qty_in_stock, 
                updated_product.min_stock_level
            ))
            
        if not updated_product.is_in_stock and product.is_in_stock:
            event_bus.publish(OutOfStockEvent(updated_product.id))
            
        return updated_product

    def toggle_product_availability(self, product_id: str) -> Optional[Product]:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            return None
            
        update_data = {"is_available": not product.is_available}
        return self.product_repository.update(product_id, update_data)
    
    def update_stock(self, product_id: str, stock_update: StockUpdateRequest) -> Optional[Product]:
        """
        Update product stock quantity and handle related events.
        
        Args:
            product_id: The product ID to update
            stock_update: StockUpdateRequest with quantity change
            
        Returns:
            Updated product or None if product not found
            
        Raises:
            ValueError: If the update would result in negative stock
        """
        product = self.product_repository.get_by_id(product_id)
        if not product:
            return None
            
        # Check if update would cause negative stock
        if product.qty_in_stock + stock_update.quantity_change < 0:
            raise ValueError("Cannot reduce stock below zero")
            
        # Use the domain model's update_stock method to apply the change and get events
        events = product.update_stock(stock_update.quantity_change)
        
        # Update last_restock_date if adding stock
        if stock_update.quantity_change > 0:
            product.last_restock_date = date.today()
            
        # Save the updated product
        updated_product = self.product_repository.update(
            product_id, 
            {
                "qty_in_stock": product.qty_in_stock,
                "last_restock_date": product.last_restock_date
            }
        )
        
        # Publish all events
        for event in events:
            event_bus.publish(event)
            
        return updated_product


class CategoryService:
    def __init__(self, category_repository: ICategoryRepository):
        self.category_repository = category_repository

    def get_category(self, category_id: str) -> Optional[Category]:
        return self.category_repository.get_by_id(category_id)

    def get_categories(self) -> List[Category]:
        return self.category_repository.get_all()

    def create_category(self, category_data: CategoryCreate) -> Category:
        # Convert to dict and add UUID
        category_dict = category_data.dict()
        category_dict["id"] = str(uuid4())
        
        return self.category_repository.create(category_dict)

    def update_category(self, category_id: str, category_data: CategoryUpdate) -> Optional[Category]:
        category = self.category_repository.get_by_id(category_id)
        if not category:
            return None
            
        update_data = category_data.dict(exclude_unset=True)
        return self.category_repository.update(category_id, update_data)

    def delete_category(self, category_id: str) -> bool:
        # Check if category has products
        category_with_products = self.category_repository.get_category_with_products(category_id)
        if category_with_products and category_with_products.products and len(category_with_products.products) > 0:
            raise ValueError("Cannot delete category with associated products")
        return self.category_repository.delete(category_id) 
"""
Product Repository Interface

This module defines interfaces for product and category repositories
to provide better adherence to the Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Protocol, Dict, Any

from ...models.product import Product, Category


class IProductRepository(Protocol):
    """Interface for Product Repository operations."""
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Product]:
        """Get a product by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Product]:
        """Get all products."""
        pass
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Product:
        """Create a new product."""
        pass
    
    @abstractmethod
    def update(self, id: str, data: Dict[str, Any]) -> Optional[Product]:
        """Update a product by ID."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a product by ID."""
        pass
    
    @abstractmethod
    def get_products_by_category(self, category_id: str) -> List[Product]:
        """Get products by category ID."""
        pass
    
    @abstractmethod
    def get_available_products(self) -> List[Product]:
        """Get all available products."""
        pass
    
    @abstractmethod
    def search_products(self, query: str) -> List[Product]:
        """Search products by name or description."""
        pass


class ICategoryRepository(Protocol):
    """Interface for Category Repository operations."""
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Category]:
        """Get a category by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Category]:
        """Get all categories."""
        pass
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Category:
        """Create a new category."""
        pass
    
    @abstractmethod
    def update(self, id: str, data: Dict[str, Any]) -> Optional[Category]:
        """Update a category by ID."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a category by ID."""
        pass
    
    @abstractmethod
    def get_category_with_products(self, category_id: str) -> Optional[Category]:
        """Get a category with its products."""
        pass 
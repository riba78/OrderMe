"""
Base Repository Module

This module defines the base repository class that all other repositories inherit from.
It provides common CRUD operations and functionality:
- Create, read, update, delete operations
- Database session management
- Common query methods

This serves as the foundation for all repositories and ensures
consistent database access patterns across the application.
"""

from typing import Type, Optional, List, Any, Dict, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from app.models.base import Base

T = TypeVar('T', bound=Base)

class BaseRepository:
    def __init__(self, model_class: Type[T], session: Session):
        self.model_class = model_class
        self.session = session

    def get_by_id(self, id: str) -> Optional[T]:
        """Get a record by ID."""
        return self.session.query(self.model_class).filter(self.model_class.id == id).first()

    def get_all(self) -> List[T]:
        """Get all records."""
        return self.session.query(self.model_class).all()

    def create(self, data: Dict[str, Any]) -> T:
        """Create a new record."""
        obj = self.model_class(**data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID."""
        obj = self.get_by_id(id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            self.session.commit()
            self.session.refresh(obj)
            return obj
        return None

    def delete(self, id: str) -> bool:
        """Delete a record by ID."""
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False

    def filter(self, **kwargs) -> List[T]:
        """Filter records by given criteria."""
        return self.session.query(self.model_class).filter_by(**kwargs).all()

    def get_paginated(self, page: int = 1, page_size: int = 10, **filters) -> tuple[List[T], int]:
        """Get paginated records with optional filters."""
        query = self.session.query(self.model_class)
        
        # Apply filters
        if filters:
            query = query.filter_by(**filters)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        results = query.offset(offset).limit(page_size).all()
        
        return results, total 
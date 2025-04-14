"""
Base Module

This module provides the base SQLAlchemy model class and common mixins.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TimestampMixin:
    """
    Mixin class that automatically adds created_at and updated_at timestamp fields
    to any model that inherits from it.
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 
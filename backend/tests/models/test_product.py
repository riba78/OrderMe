"""
Product Model Tests

This module contains unit tests for the Product and Category models.
Tests cover:
- Model validation
- Relationships
- Default values
- Business logic constraints
"""

import pytest
from uuid import uuid4
from datetime import datetime
from app.models import Product, Category
from app.schemas.product import ProductCreate, CategoryCreate

def test_create_category(test_db):
    """Test creating a new category."""
    category_id = str(uuid4())
    category = Category(
        id=category_id,
        name="Test Category",
        description="Test Description"
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)

    assert category.id == category_id
    assert category.name == "Test Category"
    assert category.description == "Test Description"
    assert isinstance(category.created_at, datetime)
    assert isinstance(category.updated_at, datetime)

def test_create_product(test_db):
    """Test creating a new product."""
    category_id = str(uuid4())
    category = Category(
        id=category_id,
        name="Test Category"
    )
    test_db.add(category)
    test_db.commit()

    product_id = str(uuid4())
    product = Product(
        id=product_id,
        name="Test Product",
        description="Test Description",
        price=99.99,
        created_by=str(uuid4()),
        category_id=category_id,
        min_stock_level=10,
        max_stock_level=100,
        qty_in_stock=50
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    assert product.id == product_id
    assert product.name == "Test Product"
    assert product.price == 99.99
    assert product.category_id == category_id
    assert product.is_available == True  # Default value
    assert product.qty_in_stock == 50
    assert isinstance(product.created_at, datetime)

def test_product_category_relationship(test_db):
    """Test the relationship between Product and Category."""
    category = Category(
        id=str(uuid4()),
        name="Test Category"
    )
    test_db.add(category)
    test_db.commit()

    product = Product(
        id=str(uuid4()),
        name="Test Product",
        price=99.99,
        created_by=str(uuid4()),
        category_id=category.id,
        min_stock_level=10,
        max_stock_level=100,
        qty_in_stock=50
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    assert product.category.id == category.id
    assert product.category.name == "Test Category"
    assert len(category.products) == 1
    assert category.products[0].id == product.id

def test_product_validation():
    """Test ProductCreate schema validation."""
    # Valid product data
    valid_data = {
        "name": "Test Product",
        "description": "Test Description",
        "price": 99.99,
        "category_id": str(uuid4()),
        "created_by": str(uuid4()),
        "min_stock_level": 10,
        "max_stock_level": 100,
        "qty_in_stock": 50
    }
    product = ProductCreate(**valid_data)
    assert product.name == valid_data["name"]
    assert product.price == valid_data["price"]

    # Test invalid price
    with pytest.raises(ValueError):
        ProductCreate(**{**valid_data, "price": -10})

    # Test invalid stock levels
    with pytest.raises(ValueError):
        ProductCreate(**{**valid_data, "min_stock_level": -1})
    
    with pytest.raises(ValueError):
        ProductCreate(**{**valid_data, "max_stock_level": -1}) 
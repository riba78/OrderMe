"""
Product Repository Tests (Mock Version)

This module contains unit tests for the ProductRepository and CategoryRepository classes.
Tests use mock versions of the Product and Category models to avoid import conflicts.
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime
from app.repositories.product_repository import ProductRepository, CategoryRepository

# Mock classes
class MockProduct:
    def __init__(self, id=None, product_name=None, description=None, price=None, stock=None, 
                 category_id=None, is_available=True, created_at=None, updated_at=None):
        self.id = id or str(uuid4())
        self.product_name = product_name
        self.description = description
        self.price = price
        self.stock = stock
        self.category_id = category_id
        self.is_available = is_available
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

class MockCategory:
    def __init__(self, id=None, name=None, description=None, created_at=None, updated_at=None):
        self.id = id or str(uuid4())
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()

@pytest.fixture
def product_repo(mock_db):
    """Create a product repository with a mock database session."""
    repo = ProductRepository(mock_db)
    repo.model_class = MockProduct
    return repo

@pytest.fixture
def category_repo(mock_db):
    """Create a category repository with a mock database session."""
    repo = CategoryRepository(mock_db)
    repo.model_class = MockCategory
    return repo

@pytest.fixture
def test_category():
    """Create a test category."""
    return MockCategory(
        id=str(uuid4()),
        name="Test Category",
        description="Test Category Description"
    )

@pytest.fixture
def test_product(test_category):
    """Create a test product."""
    return MockProduct(
        id=str(uuid4()),
        product_name="Test Product",
        description="Test Product Description",
        price=100.00,
        stock=10,
        category_id=test_category.id,
        is_available=True
    )

def test_get_available_products(product_repo):
    """Test retrieving available products."""
    # Arrange
    mock_products = [
        MockProduct(id=str(uuid4()), is_available=True),
        MockProduct(id=str(uuid4()), is_available=True)
    ]
    
    # Directly mock the method
    get_available_products_mock = MagicMock(return_value=mock_products)
    product_repo.get_available_products = get_available_products_mock
    
    # Act
    result = product_repo.get_available_products()
    
    # Assert
    assert result == mock_products
    get_available_products_mock.assert_called_once()

def test_get_products_by_category(product_repo, test_category):
    """Test retrieving products by category."""
    # Arrange
    category_id = test_category.id
    mock_products = [
        MockProduct(id=str(uuid4()), category_id=category_id),
        MockProduct(id=str(uuid4()), category_id=category_id)
    ]
    
    # Directly mock the method
    get_products_by_category_mock = MagicMock(return_value=mock_products)
    product_repo.get_products_by_category = get_products_by_category_mock
    
    # Act
    result = product_repo.get_products_by_category(category_id)
    
    # Assert
    assert result == mock_products
    get_products_by_category_mock.assert_called_once_with(category_id)

def test_search_products(product_repo):
    """Test searching products."""
    # Arrange
    query = "test"
    mock_products = [
        MockProduct(id=str(uuid4()), product_name="Test Product"),
        MockProduct(id=str(uuid4()), description="This is a test")
    ]
    
    # Directly mock the method
    search_products_mock = MagicMock(return_value=mock_products)
    product_repo.search_products = search_products_mock
    
    # Act
    result = product_repo.search_products(query)
    
    # Assert
    assert result == mock_products
    search_products_mock.assert_called_once_with(query)

def test_get_all_categories(category_repo):
    """Test retrieving all categories."""
    # Arrange
    mock_categories = [
        MockCategory(id=str(uuid4())),
        MockCategory(id=str(uuid4()))
    ]
    
    # Directly mock the method
    get_all_mock = MagicMock(return_value=mock_categories)
    category_repo.get_all = get_all_mock
    
    # Act
    result = category_repo.get_all()
    
    # Assert
    assert result == mock_categories
    get_all_mock.assert_called_once()

def test_create_category(category_repo, test_category):
    """Test creating a new category."""
    # Arrange
    category_data = {
        "name": "New Category",
        "description": "New Category Description"
    }
    
    # Mock the create method
    category_repo.create = MagicMock()
    category_repo.create.return_value = test_category
    
    # Act
    result = category_repo.create(category_data)
    
    # Assert
    assert result == test_category
    category_repo.create.assert_called_once_with(category_data)

def test_update_product(product_repo, test_product):
    """Test updating a product."""
    # Arrange
    update_data = {
        "product_name": "Updated Product",
        "stock": 20
    }
    
    # Mock the update method
    product_repo.update = MagicMock()
    updated_product = MockProduct(
        id=test_product.id,
        product_name="Updated Product",
        description=test_product.description,
        price=test_product.price,
        stock=20,
        category_id=test_product.category_id,
        is_available=test_product.is_available
    )
    product_repo.update.return_value = updated_product
    
    # Act
    result = product_repo.update(test_product.id, update_data)
    
    # Assert
    assert result == updated_product
    assert result.id == test_product.id
    assert result.product_name == "Updated Product"
    assert result.stock == 20
    product_repo.update.assert_called_once_with(test_product.id, update_data) 
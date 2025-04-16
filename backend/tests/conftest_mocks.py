"""
Test Configuration with Mocks

This module contains pytest fixtures for tests with mock repositories
that don't require a database connection.
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.user_service import UserService
from app.services.order_service import OrderService
from app.services.product_service import ProductService, CategoryService
from app.services.payment_service import PaymentService, PaymentMethodService, PaymentInfoService
from app.dependencies import (
    get_user_service,
    get_order_service,
    get_product_service,
    get_category_service,
    get_payment_service,
    get_payment_method_service,
    get_payment_info_service
)
from uuid import uuid4
from app.models.enums import UserRole, OrderStatus, PaymentStatus

class MockRepository:
    """Base mock repository that stores entities in memory."""
    
    def __init__(self):
        self.data = {}
    
    def add(self, entity):
        """Add an entity to the repository."""
        if "id" not in entity:
            entity["id"] = str(uuid4())
        self.data[entity["id"]] = entity
        return entity
    
    def get(self, entity_id):
        """Get an entity by ID."""
        return self.data.get(entity_id)
    
    def get_all(self):
        """Get all entities."""
        return list(self.data.values())
    
    def update(self, entity_id, updates):
        """Update an entity."""
        if entity_id in self.data:
            self.data[entity_id].update(updates)
            return self.data[entity_id]
        return None
    
    def delete(self, entity_id):
        """Delete an entity."""
        if entity_id in self.data:
            del self.data[entity_id]
            return True
        return False
    
    def get_by_field(self, field, value):
        """Get entities by field value."""
        return [entity for entity in self.data.values() if field in entity and entity[field] == value]

class MockPasswordHasher:
    """Mock password hasher that doesn't actually hash passwords."""
    
    def hash_password(self, password):
        """Return the password with a prefix to simulate hashing."""
        return f"hashed_{password}"
    
    def verify_password(self, plain_password, hashed_password):
        """Verify if the plain password matches the hashed password."""
        return hashed_password == f"hashed_{plain_password}"

# Make mock repository fixtures available to all tests
@pytest.fixture(scope="function")
def mock_user_repository():
    """Fixture for a mock user repository."""
    return MockRepository()

@pytest.fixture(scope="function")
def mock_order_repository():
    """Fixture for a mock order repository."""
    return MockRepository()

@pytest.fixture(scope="function")
def mock_product_repository():
    """Fixture for a mock product repository."""
    return MockRepository()

@pytest.fixture(scope="function")
def mock_category_repository():
    """Fixture for a mock category repository."""
    return MockRepository()

@pytest.fixture(scope="function")
def mock_payment_repository():
    """Fixture for a mock payment repository."""
    return MockRepository()

@pytest.fixture(scope="function")
def mock_payment_method_repository():
    """Fixture for a mock payment method repository."""
    return MockRepository()

@pytest.fixture(scope="function")
def mock_payment_info_repository():
    """Fixture for a mock payment info repository."""
    return MockRepository()

@pytest.fixture(scope="function")
def mock_password_hasher():
    """Fixture for a mock password hasher."""
    return MockPasswordHasher() 

# Mock services fixtures using the repository fixtures
@pytest.fixture(scope="function")
def mock_user_service(mock_user_repository):
    """Fixture for a mock user service."""
    service = UserService(mock_user_repository)
    return service

@pytest.fixture(scope="function")
def mock_order_service(mock_order_repository, mock_product_repository):
    """Fixture for a mock order service."""
    service = OrderService(mock_order_repository, mock_product_repository)
    return service

@pytest.fixture(scope="function")
def mock_product_service(mock_product_repository, mock_category_repository):
    """Fixture for a mock product service."""
    service = ProductService(mock_product_repository, mock_category_repository)
    return service

@pytest.fixture(scope="function")
def mock_category_service(mock_category_repository):
    """Fixture for a mock category service."""
    service = CategoryService(mock_category_repository)
    return service

@pytest.fixture(scope="function")
def mock_payment_service(mock_payment_repository, mock_payment_method_repository, mock_payment_info_repository, mock_order_repository=None):
    """Fixture for a mock payment service."""
    service = PaymentService(mock_payment_repository, mock_payment_method_repository, mock_payment_info_repository, mock_order_repository)
    return service

@pytest.fixture(scope="function")
def mock_payment_method_service(mock_payment_method_repository):
    """Fixture for a mock payment method service."""
    service = PaymentMethodService(mock_payment_method_repository)
    return service

@pytest.fixture(scope="function")
def mock_payment_info_service(mock_payment_info_repository):
    """Fixture for a mock payment info service."""
    service = PaymentInfoService(mock_payment_info_repository)
    return service

@pytest.fixture(scope="function")
def client_with_mocks(
    mock_user_service,
    mock_order_service,
    mock_product_service,
    mock_category_service,
    mock_payment_service,
    mock_payment_method_service,
    mock_payment_info_service
):
    """Create a TestClient with all services mocked."""
    # Override all service dependencies
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_order_service] = lambda: mock_order_service
    app.dependency_overrides[get_product_service] = lambda: mock_product_service
    app.dependency_overrides[get_category_service] = lambda: mock_category_service
    app.dependency_overrides[get_payment_service] = lambda: mock_payment_service
    app.dependency_overrides[get_payment_method_service] = lambda: mock_payment_method_service
    app.dependency_overrides[get_payment_info_service] = lambda: mock_payment_info_service
    
    # Create test client
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides = {} 
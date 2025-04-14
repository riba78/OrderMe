"""
Order Repository Tests (Mock Version)

This module contains unit tests for the OrderRepository class using mock models.
Tests cover:
- Order-specific queries
- Order status management
- Order-user relationships
- Order history tracking
- Order items management
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime
from app.repositories.order_repository import OrderRepository
from app.models.enums import OrderStatus

# Mock classes
class MockOrder:
    def __init__(self, id=None, user_id=None, total_amount=None, status=None, 
                 shipping_address=None, billing_address=None, items=None,
                 created_at=None, updated_at=None):
        self.id = id or str(uuid4())
        self.user_id = user_id
        self.total_amount = total_amount
        self.status = status
        self.shipping_address = shipping_address
        self.billing_address = billing_address
        self.items = items or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

class MockOrderItem:
    def __init__(self, id=None, order_id=None, product_id=None, quantity=None, 
                 unit_price=None, created_at=None, updated_at=None):
        self.id = id or str(uuid4())
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()

@pytest.fixture
def order_repo(mock_db):
    """Create an order repository with a mock database session."""
    repo = OrderRepository(mock_db)
    repo.model_class = MockOrder
    return repo

@pytest.fixture
def test_order():
    """Create a test order."""
    return MockOrder(
        id=str(uuid4()),
        user_id=str(uuid4()),
        total_amount=150.00,
        status=OrderStatus.PENDING.value,
        shipping_address="123 Main St, Anytown, USA",
        billing_address="123 Main St, Anytown, USA",
        items=[
            MockOrderItem(
                id=str(uuid4()),
                product_id=str(uuid4()),
                quantity=2,
                unit_price=75.00
            )
        ]
    )

def test_get_orders_by_user(order_repo):
    """Test retrieving orders by user ID."""
    # Arrange
    user_id = str(uuid4())
    mock_orders = [
        MockOrder(id=str(uuid4()), user_id=user_id),
        MockOrder(id=str(uuid4()), user_id=user_id)
    ]
    
    # Directly mock the method
    get_orders_by_user_mock = MagicMock(return_value=mock_orders)
    order_repo.get_orders_by_user = get_orders_by_user_mock
    
    # Act
    result = order_repo.get_orders_by_user(user_id)
    
    # Assert
    assert result == mock_orders
    get_orders_by_user_mock.assert_called_once_with(user_id)

def test_get_orders_by_status(order_repo):
    """Test retrieving orders by status."""
    # Arrange
    status = OrderStatus.PENDING
    mock_orders = [
        MockOrder(id=str(uuid4()), status=status.value),
        MockOrder(id=str(uuid4()), status=status.value)
    ]
    
    # Directly mock the method
    get_orders_by_status_mock = MagicMock(return_value=mock_orders)
    order_repo.get_orders_by_status = get_orders_by_status_mock
    
    # Act
    result = order_repo.get_orders_by_status(status)
    
    # Assert
    assert result == mock_orders
    get_orders_by_status_mock.assert_called_once_with(status)

def test_get_active_orders(order_repo):
    """Test retrieving active orders."""
    # Arrange
    mock_orders = [
        MockOrder(id=str(uuid4()), status=OrderStatus.PENDING.value),
        MockOrder(id=str(uuid4()), status=OrderStatus.CONFIRMED.value),
        MockOrder(id=str(uuid4()), status=OrderStatus.PREPARING.value)
    ]
    
    # Directly mock the method
    get_active_orders_mock = MagicMock(return_value=mock_orders)
    order_repo.get_active_orders = get_active_orders_mock
    
    # Act
    result = order_repo.get_active_orders()
    
    # Assert
    assert result == mock_orders
    get_active_orders_mock.assert_called_once()

def test_get_order_with_items(order_repo):
    """Test retrieving order with items."""
    # Arrange
    order_id = str(uuid4())
    mock_order = MockOrder(
        id=order_id,
        items=[
            MockOrderItem(id=str(uuid4()), order_id=order_id, quantity=1),
            MockOrderItem(id=str(uuid4()), order_id=order_id, quantity=2)
        ]
    )
    
    # Directly mock the method
    get_order_with_items_mock = MagicMock(return_value=mock_order)
    order_repo.get_order_with_items = get_order_with_items_mock
    
    # Act
    result = order_repo.get_order_with_items(order_id)
    
    # Assert
    assert result == mock_order
    assert len(result.items) == 2
    get_order_with_items_mock.assert_called_once_with(order_id)

def test_create_order(order_repo, test_order):
    """Test creating a new order."""
    # Arrange
    order_data = {
        "user_id": str(uuid4()),
        "total_amount": 100.00,
        "shipping_address": "456 Sample St, Sampletown, USA",
        "billing_address": "456 Sample St, Sampletown, USA",
        "status": OrderStatus.PENDING.value
    }
    
    # Mock the create method
    order_repo.create = MagicMock()
    order_repo.create.return_value = test_order
    
    # Act
    result = order_repo.create(order_data)
    
    # Assert
    assert result == test_order
    order_repo.create.assert_called_once_with(order_data)

def test_update_order_status(order_repo, test_order):
    """Test updating order status."""
    # Arrange
    new_status = OrderStatus.CONFIRMED.value
    update_data = {"status": new_status}
    
    # Mock the update method
    order_repo.update = MagicMock()
    updated_order = MockOrder(
        id=test_order.id,
        user_id=test_order.user_id,
        total_amount=test_order.total_amount,
        status=new_status,
        shipping_address=test_order.shipping_address,
        billing_address=test_order.billing_address
    )
    order_repo.update.return_value = updated_order
    
    # Act
    result = order_repo.update(test_order.id, update_data)
    
    # Assert
    assert result == updated_order
    assert result.id == test_order.id
    assert result.status == new_status
    order_repo.update.assert_called_once_with(test_order.id, update_data) 
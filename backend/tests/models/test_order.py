"""
Order Model Tests

This module contains unit tests for the Order-related models:
- Order
- OrderItem

Tests cover:
- Model validation
- Relationships
- Order status transitions
- Default values
- Business logic constraints
"""

import pytest
from uuid import uuid4
from datetime import datetime
from app.models import Order, OrderItem, OrderStatus, Product, User, UserRole
from app.schemas.order import OrderCreate, OrderItemCreate

def test_create_order(test_db):
    """Test creating a new order."""
    # Create a customer user first
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value,
        email="order_customer@example.com"
    )
    test_db.add(user)
    test_db.commit()

    order_id = str(uuid4())
    order = Order(
        id=order_id,
        user_id=user.id,
        status=OrderStatus.PENDING.value,
        total_amount=150.00,
        shipping_address="123 Test St",
        billing_address="123 Test St"
    )
    test_db.add(order)
    test_db.commit()
    test_db.refresh(order)

    assert order.id == order_id
    assert order.user_id == user.id
    assert order.status == OrderStatus.PENDING.value
    assert order.total_amount == 150.00
    assert order.shipping_address == "123 Test St"
    assert order.billing_address == "123 Test St"
    assert isinstance(order.created_at, datetime)
    assert isinstance(order.updated_at, datetime)

def test_create_order_item(test_db):
    """Test creating a new order item."""
    # Create necessary related objects
    user = User(
        id=str(uuid4()), 
        role=UserRole.CUSTOMER.value,
        email="order_item_customer@example.com"
    )
    test_db.add(user)
    test_db.commit()

    order = Order(
        id=str(uuid4()),
        user_id=user.id,
        status=OrderStatus.PENDING.value,
        total_amount=99.99
    )
    test_db.add(order)

    product = Product(
        id=str(uuid4()),
        name="Test Product",
        price=99.99,
        created_by=str(uuid4()),
        category_id=str(uuid4()),
        min_stock_level=10,
        max_stock_level=100,
        qty_in_stock=50
    )
    test_db.add(product)
    test_db.commit()

    order_item = OrderItem(
        id=str(uuid4()),
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        unit_price=99.99
    )
    test_db.add(order_item)
    test_db.commit()
    test_db.refresh(order_item)

    assert order_item.order_id == order.id
    assert order_item.product_id == product.id
    assert order_item.quantity == 2
    assert order_item.unit_price == 99.99
    assert isinstance(order_item.created_at, datetime)

def test_order_relationships(test_db):
    """Test relationships between Order and related models."""
    # Create user
    user = User(
        id=str(uuid4()), 
        role=UserRole.CUSTOMER.value,
        email="relationship_order@example.com"
    )
    test_db.add(user)
    test_db.commit()

    # Create order
    order = Order(
        id=str(uuid4()),
        user_id=user.id,
        status=OrderStatus.PENDING.value,
        total_amount=199.98
    )
    test_db.add(order)
    test_db.commit()

    # Create product
    product = Product(
        id=str(uuid4()),
        name="Test Product",
        price=99.99,
        created_by=str(uuid4()),
        category_id=str(uuid4()),
        min_stock_level=10,
        max_stock_level=100,
        qty_in_stock=50
    )
    test_db.add(product)
    test_db.commit()

    # Create order items
    order_item = OrderItem(
        id=str(uuid4()),
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        unit_price=99.99
    )
    test_db.add(order_item)
    test_db.commit()

    # Test relationships
    assert len(order.items) == 1
    assert order.items[0].product_id == product.id
    assert order.user_id == user.id
    assert order_item.order.user_id == user.id
    assert order_item.product.name == "Test Product"

def test_order_status_transitions(test_db):
    """Test order status transitions."""
    user = User(
        id=str(uuid4()), 
        role=UserRole.CUSTOMER.value,
        email="status_transitions@example.com"
    )
    test_db.add(user)
    test_db.commit()

    order = Order(
        id=str(uuid4()),
        user_id=user.id,
        status=OrderStatus.PENDING.value,
        total_amount=99.99
    )
    test_db.add(order)
    test_db.commit()

    # Test valid status transitions
    valid_transitions = [
        OrderStatus.CONFIRMED,
        OrderStatus.PREPARING,
        OrderStatus.READY,
        OrderStatus.DELIVERED
    ]

    for status in valid_transitions:
        order.order_status = status
        test_db.commit()
        test_db.refresh(order)
        assert order.order_status == status

def test_order_validation():
    """Test OrderCreate schema validation."""
    valid_data = {
        "user_id": str(uuid4()),
        "total_amount": 150.00,
        "shipping_address": "123 Test St",
        "billing_address": "123 Test St",
        "status": OrderStatus.PENDING
    }
    order = OrderCreate(**valid_data)
    assert order.total_amount == valid_data["total_amount"]
    assert order.shipping_address == valid_data["shipping_address"]

    # Test invalid total amount
    with pytest.raises(ValueError):
        OrderCreate(**{**valid_data, "total_amount": -10})

def test_order_item_validation():
    """Test OrderItemCreate schema validation."""
    valid_data = {
        "order_id": str(uuid4()),
        "product_id": str(uuid4()),
        "quantity": 2,
        "unit_price": 99.99
    }
    order_item = OrderItemCreate(**valid_data)
    assert order_item.quantity == valid_data["quantity"]
    assert order_item.unit_price == valid_data["unit_price"]

    # Test invalid quantity
    with pytest.raises(ValueError):
        OrderItemCreate(**{**valid_data, "quantity": 0})

    # Test invalid unit price
    with pytest.raises(ValueError):
        OrderItemCreate(**{**valid_data, "unit_price": -1}) 
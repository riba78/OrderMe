"""
Order Model Tests

This module tests the Order and OrderItem models:
- Creating orders and order items
- Order status transitions
- Relationships between orders, users, and products
"""

import pytest
from uuid import uuid4
from datetime import datetime
from app.models import User, AdminManager, Order, OrderItem, Product, Category, UserRole, OrderStatus

def test_create_order(test_db):
    """Test creating a new order."""
    # Create a customer user first
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value
    )
    test_db.add(user)
    test_db.commit()

    admin = AdminManager(
        user_id=user.id,
        email="order_customer@example.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    test_db.add(admin)
    test_db.commit()

    # Create an order
    order_id = str(uuid4())
    order = Order(
        id=order_id,
        user_id=user.id,
        status=OrderStatus.PENDING.value,
        total_amount=99.99
    )
    test_db.add(order)
    test_db.commit()
    test_db.refresh(order)

    assert order.id == order_id
    assert order.user_id == user.id
    assert order.status == OrderStatus.PENDING.value
    assert float(order.total_amount) == 99.99
    assert isinstance(order.created_at, datetime)

def test_create_order_item(test_db):
    """Test creating a new order item."""
    # Create necessary related objects
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value
    )
    test_db.add(user)
    test_db.commit()

    admin = AdminManager(
        user_id=user.id,
        email="order_item_customer@example.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    test_db.add(admin)
    test_db.commit()

    # Create product
    product = Product(
        id=str(uuid4()),
        product_name="Test Product",
        price=9.99,
        created_by=user.id,
        min_stock_level=10,
        max_stock_level=100,
        qty_in_stock=50
    )
    test_db.add(product)
    test_db.commit()

    # Create order
    order = Order(
        id=str(uuid4()),
        user_id=user.id,
        status=OrderStatus.PENDING.value,
        total_amount=19.98  # 2 * 9.99
    )
    test_db.add(order)
    test_db.commit()

    # Create order item
    order_item = OrderItem(
        id=str(uuid4()),
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        unit_price=9.99
    )
    test_db.add(order_item)
    test_db.commit()
    test_db.refresh(order_item)

    assert order_item.order_id == order.id
    assert order_item.product_id == product.id
    assert order_item.quantity == 2
    assert float(order_item.unit_price) == 9.99

def test_order_relationships(test_db):
    """Test relationships between Order and related models."""
    # Create user
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value
    )
    test_db.add(user)
    test_db.commit()
    
    admin = AdminManager(
        user_id=user.id,
        email="relationship_order@example.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    test_db.add(admin)
    test_db.commit()

    # Create product
    product = Product(
        id=str(uuid4()),
        product_name="Test Product",
        price=9.99,
        created_by=user.id,
        min_stock_level=10,
        max_stock_level=100,
        qty_in_stock=50
    )
    test_db.add(product)
    test_db.commit()

    # Create order
    order = Order(
        id=str(uuid4()),
        user_id=user.id,
        status=OrderStatus.PENDING.value,
        total_amount=19.98
    )
    test_db.add(order)
    test_db.commit()

    # Create order item
    order_item = OrderItem(
        id=str(uuid4()),
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        unit_price=9.99
    )
    test_db.add(order_item)
    test_db.commit()

    # Test relationships
    test_db.refresh(order)
    test_db.refresh(user)
    assert len(order.items) == 1
    assert order.items[0].product_id == product.id
    assert len(user.orders) == 1
    assert user.orders[0].id == order.id

def test_order_status_transitions(test_db):
    """Test order status transitions."""
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value
    )
    test_db.add(user)
    test_db.commit()
    
    admin = AdminManager(
        user_id=user.id,
        email="status_transitions@example.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    test_db.add(admin)
    test_db.commit()

    # Create order with initial PENDING status
    order = Order(
        id=str(uuid4()),
        user_id=user.id,
        status=OrderStatus.PENDING.value,
        total_amount=99.99
    )
    test_db.add(order)
    test_db.commit()
    test_db.refresh(order)

    assert order.status == OrderStatus.PENDING.value
    
    # Update to CONFIRMED
    order.status = OrderStatus.CONFIRMED.value
    test_db.commit()
    test_db.refresh(order)
    assert order.status == OrderStatus.CONFIRMED.value
    
    # Update to PREPARING
    order.status = OrderStatus.PREPARING.value
    test_db.commit()
    test_db.refresh(order)
    assert order.status == OrderStatus.PREPARING.value
    
    # Update to DELIVERED  
    order.status = OrderStatus.DELIVERED.value
    test_db.commit()
    test_db.refresh(order)
    assert order.status == OrderStatus.DELIVERED.value

def test_order_validation():
    """Test OrderCreate schema validation."""
    # Import here to avoid circular imports in test
    from app.schemas.order import OrderCreate, OrderItemCreate
    
    valid_data = {
        "user_id": str(uuid4()),
        "total_amount": 99.99,
        "status": OrderStatus.PENDING,
        "shipping_address": "123 Test St, Test City",
        "billing_address": "123 Test St, Test City",
        "items": [
            {
                "product_id": str(uuid4()),
                "quantity": 2,
                "unit_price": 49.99
            }
        ]
    }
    order = OrderCreate(**valid_data)
    assert order.total_amount == 99.99
    assert order.status == OrderStatus.PENDING
    assert len(order.items) == 1
    assert order.items[0].quantity == 2
    assert order.items[0].unit_price == 49.99

def test_order_item_validation():
    """Test OrderItemCreate schema validation."""
    # Import here to avoid circular imports in test
    from app.schemas.order import OrderItemCreate
    
    valid_data = {
        "product_id": str(uuid4()),
        "quantity": 2,
        "unit_price": 9.99
    }
    order_item = OrderItemCreate(**valid_data)
    assert order_item.quantity == 2
    assert order_item.unit_price == 9.99 
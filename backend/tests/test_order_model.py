"""
Order Model Tests

These tests verify that the Order models can be imported correctly.
"""

import pytest

def test_order_imports():
    """Test that Order models can be imported correctly."""
    # Import inside the test to avoid circular imports
    from app.models.order import Order, OrderItem
    assert Order is not None
    assert OrderItem is not None
    
    # Test creating an Order instance
    order = Order(
        user_id="123",
        status="pending",
        total_amount=100.0
    )
    assert order.user_id == "123"
    assert order.status == "pending"
    assert order.total_amount == 100.0
    
    # Test creating an OrderItem instance
    order_item = OrderItem(
        order_id="456",
        product_id="789",
        quantity=2,
        unit_price=50.0
    )
    assert order_item.order_id == "456"
    assert order_item.product_id == "789"
    assert order_item.quantity == 2
    assert order_item.unit_price == 50.0 
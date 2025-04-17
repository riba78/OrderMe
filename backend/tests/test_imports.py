"""
Import Tests

These tests verify that model imports work correctly.
"""

import pytest

def test_basic_imports():
    """Test that basic model imports work."""
    # Import models one by one to avoid circular imports
    from app.models.user import User
    from app.models.product import Category, Product
    from app.models.notification import Notification
    from app.models.enums import UserRole, OrderStatus, PaymentStatus, NotificationType
    from app.models.payment import Payment, PaymentMethod, PaymentInfo
    
    # Only test that imports work, don't create instances
    assert User.__name__ == "User"
    assert Category.__name__ == "Category"
    assert Product.__name__ == "Product"
    assert Notification.__name__ == "Notification"
    assert Payment.__name__ == "Payment"
    assert PaymentMethod.__name__ == "PaymentMethod"
    assert PaymentInfo.__name__ == "PaymentInfo"
    
    # Test enums
    assert UserRole.CUSTOMER.value == "customer"
    assert OrderStatus.PENDING.value == "pending"
    assert PaymentStatus.PENDING.value == "pending"
    assert NotificationType.SYSTEM.value == "system"
    
def test_order_imports():
    """Test that order model imports work."""
    # Import the order models in isolation
    from app.models.order import Order, OrderItem
    assert Order.__name__ == "Order"
    assert OrderItem.__name__ == "OrderItem" 
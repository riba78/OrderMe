"""
Mock Controller Tests

These tests mock the controllers without requiring a database connection.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.controllers.user_controller import router as user_router
from app.controllers.order_controller import router as order_router
from app.controllers.payment_controller import router as payment_router
from app.models.enums import UserRole, OrderStatus, PaymentStatus

def test_user_controller_import():
    """Test that user controller can be imported."""
    assert user_router is not None
    assert user_router.prefix == ""  # Router prefix is set in main.py
    
    # Check that endpoints are defined
    endpoint_paths = [route.path for route in user_router.routes]
    assert "/test" in endpoint_paths
    assert "/me" in endpoint_paths
    assert "/users/" in endpoint_paths
    assert "/users/{user_id}" in endpoint_paths

def test_order_controller_import():
    """Test that order controller can be imported."""
    assert order_router is not None
    assert order_router.prefix == ""  # Router prefix is set in main.py
    
    # Check that endpoints are defined
    endpoint_paths = [route.path for route in order_router.routes]
    assert "/test" in endpoint_paths
    assert "/" in endpoint_paths
    assert "/{order_id}" in endpoint_paths
    assert "/{order_id}/status" in endpoint_paths
    assert "/{order_id}/cancel" in endpoint_paths

def test_payment_controller_import():
    """Test that payment controller can be imported."""
    assert payment_router is not None
    assert payment_router.prefix == ""  # Router prefix is set in main.py
    
    # Check that endpoints are defined
    endpoint_paths = [route.path for route in payment_router.routes]
    assert "/test" in endpoint_paths
    assert "/payments/" in endpoint_paths
    assert "/payments/{payment_id}" in endpoint_paths 
"""
Controller Tests with Mocks

These tests verify that the controllers work correctly
without requiring a database connection.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.controllers.user_controller import router as user_router
from app.controllers.order_controller import router as order_router
from app.controllers.payment_controller import router as payment_router
from app.models.enums import UserRole, OrderStatus, PaymentStatus

# Create a test app with our routers
test_app = FastAPI()
test_app.include_router(user_router, prefix="/api/users")
test_app.include_router(order_router, prefix="/api/orders")
test_app.include_router(payment_router, prefix="/api/payments")

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(test_app)

# User Controller Tests
class TestUserController:
    """Test the user controller endpoints without database connections."""
    
    def test_user_test_endpoint(self, client):
        """Test the test endpoint in user controller."""
        with patch('app.controllers.user_controller.get_db'):
            response = client.get("/api/users/test")
            assert response.status_code == 200
            assert response.json() == {"message": "User controller is working"}

# Order Controller Tests
class TestOrderController:
    """Test the order controller endpoints without database connections."""
    
    def test_order_test_endpoint(self, client):
        """Test the test endpoint in order controller."""
        with patch('app.controllers.order_controller.get_db'):
            response = client.get("/api/orders/test")
            assert response.status_code == 200
            assert response.json() == {"message": "Order controller is working"}

# Payment Controller Tests
class TestPaymentController:
    """Test the payment controller endpoints without database connections."""
    
    def test_payment_test_endpoint(self, client):
        """Test the test endpoint in payment controller."""
        with patch('app.controllers.payment_controller.get_db'):
            response = client.get("/api/payments/test")
            assert response.status_code == 200
            assert response.json() == {"message": "Payment controller is working"} 
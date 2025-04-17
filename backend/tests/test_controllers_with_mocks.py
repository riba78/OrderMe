"""
Controller Tests with Mocks

These tests verify that the controllers work correctly using mock repositories
instead of a real database connection.
"""

import pytest
from fastapi.testclient import TestClient
from app.models.enums import UserRole, OrderStatus, PaymentStatus
from uuid import uuid4

# Import fixtures directly to ensure they're available
pytestmark = pytest.mark.usefixtures(
    "mock_user_repository",
    "mock_order_repository",
    "mock_product_repository",
    "mock_payment_repository",
    "mock_user_service",
    "mock_order_service",
    "mock_product_service",
    "mock_payment_service",
    "client_with_mocks"
)

class TestUserController:
    """Test the user controller endpoints with mock repositories."""
    
    def test_user_test_endpoint(self, client_with_mocks):
        """Test the test endpoint."""
        response = client_with_mocks.get("/users/test")
        assert response.status_code == 200
        assert response.json() == {"message": "User controller is working"}
    
    def test_get_users_empty(self, client_with_mocks, mock_user_repository):
        """Test getting users when none exist."""
        response = client_with_mocks.get("/users/users/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_and_get_user(self, client_with_mocks, mock_user_repository):
        """Test creating and then getting a user."""
        # Create a test user
        user_data = {
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User",
            "role": UserRole.CUSTOMER.value
        }
        
        # Create the user
        response = client_with_mocks.post("/users/users/", json=user_data)
        assert response.status_code == 201
        created_user = response.json()
        assert created_user["email"] == user_data["email"]
        assert created_user["full_name"] == user_data["full_name"]
        
        # Get the user
        user_id = created_user["id"]
        response = client_with_mocks.get(f"/users/users/{user_id}")
        assert response.status_code == 200
        retrieved_user = response.json()
        assert retrieved_user["id"] == user_id
        assert retrieved_user["email"] == user_data["email"]
    
    def test_get_users_by_role(self, client_with_mocks, mock_user_repository):
        """Test getting users by role."""
        # Create some test users with different roles
        user1 = {
            "id": str(uuid4()),
            "email": "customer@example.com",
            "password": "password1",
            "full_name": "Customer User",
            "role": UserRole.CUSTOMER.value
        }
        user2 = {
            "id": str(uuid4()),
            "email": "admin@example.com",
            "password": "password2",
            "full_name": "Admin User",
            "role": UserRole.ADMIN.value
        }
        
        # Add users to repository
        mock_user_repository.add(user1)
        mock_user_repository.add(user2)
        
        # Get users by role
        response = client_with_mocks.get(f"/users/users/role/{UserRole.CUSTOMER.value}")
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 1
        assert users[0]["email"] == user1["email"]

class TestOrderController:
    """Test the order controller endpoints with mock repositories."""
    
    def test_order_test_endpoint(self, client_with_mocks):
        """Test the test endpoint."""
        response = client_with_mocks.get("/orders/test")
        assert response.status_code == 200
        assert response.json() == {"message": "Order controller is working"}
    
    def test_get_orders_empty(self, client_with_mocks, mock_order_repository):
        """Test getting orders when none exist."""
        response = client_with_mocks.get("/orders/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_and_get_order(self, client_with_mocks, mock_order_repository, mock_user_repository):
        """Test creating and then getting an order."""
        # Create a test user
        user = {
            "id": "1",
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User",
            "role": UserRole.CUSTOMER.value
        }
        mock_user_repository.add(user)
        
        # Create a test order
        order_data = {
            "user_id": "1",
            "status": OrderStatus.PENDING.value,
            "total_amount": 100.0,
            "items": [
                {"product_id": "1", "quantity": 2, "price": 50.0}
            ]
        }
        
        # Create the order
        response = client_with_mocks.post("/orders/", json=order_data)
        assert response.status_code == 201
        created_order = response.json()
        assert created_order["user_id"] == order_data["user_id"]
        assert created_order["status"] == order_data["status"]
        
        # Get the order
        order_id = created_order["id"]
        response = client_with_mocks.get(f"/orders/{order_id}")
        assert response.status_code == 200
        retrieved_order = response.json()
        assert retrieved_order["id"] == order_id
        assert retrieved_order["user_id"] == order_data["user_id"]

class TestPaymentController:
    """Test the payment controller endpoints with mock repositories."""
    
    def test_payment_test_endpoint(self, client_with_mocks):
        """Test the test endpoint."""
        response = client_with_mocks.get("/payments/test")
        assert response.status_code == 200
        assert response.json() == {"message": "Payment controller is working"}
    
    def test_get_payments_empty(self, client_with_mocks, mock_payment_repository):
        """Test getting payments when none exist."""
        response = client_with_mocks.get("/payments/payments/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_and_get_payment(self, client_with_mocks, mock_payment_repository, mock_order_repository):
        """Test creating and then getting a payment."""
        # Create a test order
        order = {
            "id": "1",
            "user_id": "1",
            "status": OrderStatus.PENDING.value,
            "total_amount": 100.0
        }
        mock_order_repository.add(order)
        
        # Create a test payment
        payment_data = {
            "order_id": "1",
            "amount": 100.0,
            "status": PaymentStatus.PENDING.value,
            "payment_method": "credit_card"
        }
        
        # Create the payment
        response = client_with_mocks.post("/payments/payments/", json=payment_data)
        assert response.status_code == 201
        created_payment = response.json()
        assert created_payment["order_id"] == payment_data["order_id"]
        assert created_payment["amount"] == payment_data["amount"]
        
        # Get the payment
        payment_id = created_payment["id"]
        response = client_with_mocks.get(f"/payments/payments/{payment_id}")
        assert response.status_code == 200
        retrieved_payment = response.json()
        assert retrieved_payment["id"] == payment_id
        assert retrieved_payment["order_id"] == payment_data["order_id"] 
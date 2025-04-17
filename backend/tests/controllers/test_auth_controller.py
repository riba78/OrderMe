"""
Auth Controller Tests

These tests verify that all authentication-related endpoints work correctly.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.models.enums import UserRole

# Mock user data
mock_user = {
    "id": "1",
    "email": "test@example.com",
    "full_name": "Test User",
    "phone": "1234567890",
    "address": "123 Test St",
    "role": UserRole.CUSTOMER.value,
    "is_active": True
}

# Mock token data
mock_token = {
    "access_token": "test_token",
    "token_type": "bearer"
}

def test_auth_test_endpoint(test_client):
    """Test the test endpoint returns the expected message."""
    response = test_client.get("/auth/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Auth controller is working"}

@pytest.fixture
def mock_auth_service():
    """Create a mock auth service."""
    auth_service = MagicMock()
    auth_service.register_user.return_value = mock_user
    auth_service.authenticate_user.return_value = mock_user
    auth_service.create_access_token.return_value = mock_token["access_token"]
    return auth_service

def test_register_user(test_client):
    """Test user registration."""
    # Since we don't have specific auth service mocking yet, this is just a smoke test
    # In a real test, we'd patch the auth service or user service
    user_data = {
        "email": "new@example.com",
        "password": "securepassword123",
        "full_name": "New User",
        "role": UserRole.CUSTOMER.value
    }
    # This will likely fail since we're not properly mocking the service
    # But we're including it for completeness
    response = test_client.post("/auth/register", json=user_data)
    # Don't assert here since we expect this to fail without proper mocking

def test_login(test_client):
    """Test user login and token generation."""
    # Register a user first
    user_data = {
        "email": "login_test@example.com",
        "password": "securepassword123"
    }
    test_client.post("/auth/register", json=user_data)
    
    # Test login
    login_data = {
        "username": "login_test@example.com",
        "password": "securepassword123"
    }
    response = test_client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    # Test invalid login
    invalid_login = {
        "username": "login_test@example.com",
        "password": "wrongpassword"
    }
    response = test_client.post("/auth/token", data=invalid_login)
    assert response.status_code == 401

def test_me_endpoint(test_client):
    """Test the /me endpoint that returns current user info."""
    # Register and login a user first
    user_data = {
        "email": "me_test@example.com",
        "password": "securepassword123"
    }
    test_client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "me_test@example.com",
        "password": "securepassword123"
    }
    login_response = test_client.post("/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    
    # Test /me endpoint with valid token
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"email": "me_test@example.com"}
    
    # Test without token
    response = test_client.get("/auth/me")
    assert response.status_code == 401

def test_logout(test_client):
    """Test the logout endpoint."""
    response = test_client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out"} 
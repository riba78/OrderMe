"""
User Controller Tests

These tests verify that all user-related endpoints work correctly.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.models.enums import UserRole
from app.utils.json_encoder import serialize_enum

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

mock_admin = {
    "id": "2",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "phone": "0987654321",
    "address": "456 Admin St",
    "role": UserRole.ADMIN.value,
    "is_active": True
}

def test_user_test_endpoint(test_client):
    """Test the test endpoint returns the expected message."""
    response = test_client.get("/users/test")
    assert response.status_code == 200
    assert response.json() == {"message": "User controller is working"}

def setup_mock_user_service(mock_service):
    """Configure the mock user service with test data."""
    mock_service.get_users.return_value = [mock_user, mock_admin]
    mock_service.get_user.return_value = mock_user
    mock_service.create_user.return_value = mock_user
    mock_service.update_user.return_value = mock_user
    mock_service.delete_user.return_value = True
    mock_service.get_users_by_role.return_value = [mock_user]
    return mock_service

@pytest.fixture
def authenticated_client(test_client):
    """Create a test client with authentication."""
    # For now, we'll just return the test client without authentication
    # In a real scenario, we would set up JWT token generation
    return test_client

def test_get_users(test_client, mock_user_service):
    """Test getting all users."""
    setup_mock_user_service(mock_user_service)
    response = test_client.get("/users/users/")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["email"] == mock_user["email"]
    assert mock_user_service.get_users.called

def test_get_user_by_id(test_client, mock_user_service):
    """Test getting a user by ID."""
    setup_mock_user_service(mock_user_service)
    response = test_client.get("/users/users/1")
    assert response.status_code == 200
    assert response.json()["email"] == mock_user["email"]
    mock_user_service.get_user.assert_called_with("1")
    
    # Test non-existent user
    mock_user_service.get_user.return_value = None
    response = test_client.get("/users/users/999")
    assert response.status_code == 404

def test_create_user(test_client, mock_user_service):
    """Test creating a user."""
    setup_mock_user_service(mock_user_service)
    user_data = {
        "email": "new@example.com",
        "password": "password123",
        "full_name": "New User",
        "role": UserRole.CUSTOMER.value
    }
    response = test_client.post("/users/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == mock_user["email"]
    mock_user_service.create_user.assert_called_once()
    
    # Test creating user with existing email
    mock_user_service.create_user.side_effect = ValueError("Email already registered")
    response = test_client.post("/users/users/", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_update_user(test_client, mock_user_service):
    """Test updating a user."""
    setup_mock_user_service(mock_user_service)
    update_data = {
        "full_name": "Updated User",
        "phone": "5555555555"
    }
    response = test_client.put("/users/users/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["email"] == mock_user["email"]
    
    # Test updating non-existent user
    mock_user_service.update_user.return_value = None
    response = test_client.put("/users/users/999", json=update_data)
    assert response.status_code == 404

def test_delete_user(test_client, mock_user_service):
    """Test deleting a user."""
    setup_mock_user_service(mock_user_service)
    response = test_client.delete("/users/users/1")
    assert response.status_code == 200
    assert response.json() == {"message": "User deleted successfully"}
    mock_user_service.delete_user.assert_called_with("1")
    
    # Test deleting non-existent user
    mock_user_service.delete_user.return_value = False
    response = test_client.delete("/users/users/999")
    assert response.status_code == 404
    
    # Test deleting with error
    mock_user_service.delete_user.side_effect = ValueError("Cannot delete admin")
    response = test_client.delete("/users/users/1")
    assert response.status_code == 400
    assert "Cannot delete admin" in response.json()["detail"]

def test_get_users_by_role(test_client, mock_user_service):
    """Test getting users by role."""
    setup_mock_user_service(mock_user_service)
    response = test_client.get(f"/users/users/role/{UserRole.CUSTOMER.value}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["email"] == mock_user["email"]
    assert mock_user_service.get_users_by_role.called

@pytest.mark.skip(reason="Requires real authentication")
def test_user_profile(authenticated_client):
    """Test getting the current user's profile."""
    # This test requires a real authenticated session
    response = authenticated_client.get("/users/me")
    assert response.status_code == 200
    assert "email" in response.json()
    
    # Test without authentication
    unauthenticated_client = authenticated_client.copy()
    unauthenticated_client.headers = {}
    response = unauthenticated_client.get("/users/me")
    assert response.status_code == 401 
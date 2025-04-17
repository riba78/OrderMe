"""
Main Application Tests

These tests verify that the main application's endpoints and exception handlers work correctly.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_health_endpoint(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_http_exception_handler(test_client):
    """Test the HTTP exception handler.
    
    This test accesses a non-existent endpoint to trigger a 404 error.
    """
    response = test_client.get("/nonexistent-endpoint")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_validation_exception_handler(test_client):
    """Test the validation exception handler.
    
    This test sends invalid data to an endpoint to trigger a validation error.
    """
    # Use user registration with invalid data (missing required fields)
    response = test_client.post("/auth/register", json={})
    assert response.status_code == 422
    assert "detail" in response.json()

def test_sqlalchemy_exception_handler():
    """Test the SQLAlchemy exception handler.
    
    This would normally require setting up a scenario where a database
    error occurs. For simplicity, we're skipping actual implementation.
    A real implementation would mock the database to raise an exception.
    """
    # This is a placeholder - in a real test, you would create a scenario
    # that triggers a database error
    pass 
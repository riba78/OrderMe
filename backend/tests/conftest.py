"""
Test Configuration

This module contains pytest fixtures and configuration for all tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.base import Base
from app.database import get_db
from app.dependencies import get_user_service, get_product_service, get_category_service, get_order_service, get_payment_service
from fastapi.testclient import TestClient
from app.main import app
from typing import Generator
from contextlib import contextmanager
from unittest.mock import MagicMock

# Import all fixtures from conftest_mocks.py
from .conftest_mocks import (
    mock_user_repository,
    mock_order_repository,
    mock_product_repository,
    mock_category_repository,
    mock_payment_repository,
    mock_payment_method_repository,
    mock_payment_info_repository,
    mock_password_hasher,
    mock_user_service,
    mock_order_service,
    mock_product_service,
    mock_category_service,
    mock_payment_service,
    mock_payment_method_service,
    mock_payment_info_service,
    client_with_mocks
)

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_db dependency
@contextmanager
def override_get_db(test_db):
    """Override the get_db dependency with test_db for testing."""
    def _get_test_db():
        try:
            yield test_db
        finally:
            pass  # We'll close it in the test_db fixture
    
    original = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = _get_test_db
    try:
        yield
    finally:
        app.dependency_overrides = original

@pytest.fixture
def test_client(test_db):
    """Create a FastAPI TestClient for testing API endpoints."""
    # Override the get_db dependency with our test_db
    def _get_test_db():
        try:
            yield test_db
        finally:
            pass  # We'll close it in the test_db fixture
    
    app.dependency_overrides[get_db] = _get_test_db
    
    # Create test client
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides = {}

@pytest.fixture
def auth_token():
    """Generate a test authentication token.
    
    This is a placeholder. In real tests, you would create an actual token
    by authenticating a test user.
    """
    return "test_token" 
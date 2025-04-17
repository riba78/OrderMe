"""
Controller Tests Configuration

This module contains pytest fixtures specifically for controller tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.base import Base
from app.database import get_db
from app.dependencies import (
    get_user_service, 
    get_product_service, 
    get_category_service, 
    get_order_service, 
    get_payment_service
)
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock

# Test database setup
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

@pytest.fixture
def mock_user_service():
    """Create a mock user service."""
    mock = MagicMock()
    app.dependency_overrides[get_user_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_user_service, None)

@pytest.fixture
def mock_product_service():
    """Create a mock product service."""
    mock = MagicMock()
    app.dependency_overrides[get_product_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_product_service, None)

@pytest.fixture
def mock_category_service():
    """Create a mock category service."""
    mock = MagicMock()
    app.dependency_overrides[get_category_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_category_service, None)

@pytest.fixture
def mock_order_service():
    """Create a mock order service."""
    mock = MagicMock()
    app.dependency_overrides[get_order_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_order_service, None)

@pytest.fixture
def mock_payment_service():
    """Create a mock payment service."""
    mock = MagicMock()
    app.dependency_overrides[get_payment_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_payment_service, None)

@pytest.fixture
def test_client(test_db):
    """Create a FastAPI TestClient that uses the test database."""
    def _get_test_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = _get_test_db
    
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides = {} 
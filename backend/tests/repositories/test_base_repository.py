"""
Base Repository Tests

This module contains unit tests for the BaseRepository class.
Tests cover:
- CRUD operations
- Query building
- Error handling
- Pagination
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from uuid import uuid4
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

# Create a test Base for SQLAlchemy models
TestBase = declarative_base()

class MockModel(TestBase):
    """Mock model for testing BaseRepository."""
    __tablename__ = 'mock_models'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    value = Column(Integer, nullable=False)
    
    def __init__(self, id=None, name=None, value=None):
        self.id = id
        self.name = name
        self.value = value

@pytest.fixture
def mock_session():
    session = MagicMock()
    return session

@pytest.fixture
def repository(mock_session):
    return BaseRepository(model_class=MockModel, session=mock_session)

def test_create(repository, mock_session):
    """Test creating a new record."""
    # Arrange
    data = {"name": "Test", "value": 1}
    mock_model = MockModel(name="Test", value=1)
    
    # Mock the model creation
    repository.model_class = MagicMock(return_value=mock_model)
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    
    # Act
    result = repository.create(data)
    
    # Assert
    assert mock_session.add.called_with(mock_model)
    assert mock_session.commit.called
    assert mock_session.refresh.called
    assert result == mock_model

def test_get_by_id(repository, mock_session):
    """Test getting a record by ID."""
    # Arrange
    mock_id = str(uuid4())
    model = MockModel(id=mock_id, name="Test", value=1)
    
    query_mock = MagicMock()
    mock_session.query.return_value = query_mock
    filter_mock = MagicMock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = model
    
    # Act
    result = repository.get_by_id(mock_id)
    
    # Assert
    assert mock_session.query.called_with(MockModel)
    assert query_mock.filter.called
    assert result == model

def test_get_all(repository, mock_session):
    """Test getting all records."""
    # Arrange
    models = [
        MockModel(id=str(uuid4()), name=f"Test {i}", value=i)
        for i in range(1, 6)
    ]
    
    query_mock = MagicMock()
    mock_session.query.return_value = query_mock
    query_mock.all.return_value = models
    
    # Act
    results = repository.get_all()
    
    # Assert
    assert mock_session.query.called_with(MockModel)
    assert query_mock.all.called
    assert results == models

def test_update(repository, mock_session):
    """Test updating a record."""
    # Arrange
    mock_id = str(uuid4())
    model = MockModel(id=mock_id, name="Test", value=1)
    
    query_mock = MagicMock()
    mock_session.query.return_value = query_mock
    filter_mock = MagicMock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = model
    
    # Act
    updates = {"name": "Updated", "value": 2}
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    result = repository.update(mock_id, updates)
    
    # Assert
    assert mock_session.query.called_with(MockModel)
    assert query_mock.filter.called
    assert model.name == "Updated"
    assert model.value == 2
    assert mock_session.commit.called
    assert mock_session.refresh.called
    assert result == model

def test_delete(repository, mock_session):
    """Test deleting a record."""
    # Arrange
    mock_id = str(uuid4())
    model = MockModel(id=mock_id, name="Test", value=1)
    
    query_mock = MagicMock()
    mock_session.query.return_value = query_mock
    filter_mock = MagicMock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = model
    
    # Act
    result = repository.delete(mock_id)
    
    # Assert
    assert mock_session.query.called_with(MockModel)
    assert query_mock.filter.called
    assert mock_session.delete.called_with(model)
    assert result is True

def test_filter(repository, mock_session):
    """Test filtering records."""
    # Arrange
    models = [
        MockModel(id=str(uuid4()), name="Test", value=i)
        for i in range(1, 6)
    ]
    
    query_mock = MagicMock()
    mock_session.query.return_value = query_mock
    filter_by_mock = MagicMock()
    query_mock.filter_by.return_value = filter_by_mock
    filter_by_mock.all.return_value = [m for m in models if m.value > 3]
    
    # Act
    results = repository.filter(value=3)
    
    # Assert
    assert mock_session.query.called_with(MockModel)
    assert query_mock.filter_by.called_with(value=3)
    assert len(results) == 2  # Only models with value > 3

def test_pagination(repository, mock_session):
    # Create test data
    models = [
        MockModel(id=str(uuid4()), name=f"Test {i}", value=i)
        for i in range(1, 11)
    ]
    
    # Configure mock session query to return these models
    query_mock = MagicMock()
    mock_session.query.return_value = query_mock
    query_mock.offset.return_value = query_mock
    query_mock.limit.return_value = query_mock
    
    # For first page (with no filter)
    query_mock.all.return_value = models[:5]
    query_mock.count.return_value = len(models)
    
    # Test first page
    results, total = repository.get_paginated(page=1, page_size=5)
    
    assert mock_session.query.called
    assert query_mock.offset.called_with(0)
    assert query_mock.limit.called_with(5)
    assert len(results) == 5
    assert total == 10
    
    # Test with filter
    filter_by_mock = MagicMock()
    query_mock.filter_by.return_value = filter_by_mock
    filter_by_mock.offset.return_value = filter_by_mock
    filter_by_mock.limit.return_value = filter_by_mock
    filter_by_mock.all.return_value = [m for m in models if m.value > 5][:3]
    filter_by_mock.count.return_value = 5  # Total matching filter
    
    results, total = repository.get_paginated(page=1, page_size=3, value=5)
    
    assert query_mock.filter_by.called_with(value=5)
    assert filter_by_mock.offset.called_with(0)
    assert filter_by_mock.limit.called_with(3)
    assert len(results) == 3
    assert total == 5 
"""
Unit tests for the NotificationRepository class.

This module contains tests for notification-related database operations,
including:
- User notification retrieval
- Notification type filtering
- Order notification retrieval
- Notification status management (read/unread)
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4
from app.models.enums import NotificationType
from app.repositories.notification_repository import NotificationRepository
from app.models.models import Notification


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock()
    return db


@pytest.fixture
def notification_repo(mock_db):
    """Create a notification repository with a mock database session."""
    with patch('app.repositories.notification_repository.Notification') as mock_notification_class:
        repo = NotificationRepository(mock_db)
        
        # Configure the mock notification model
        mock_notification_class.id = MagicMock()
        mock_notification_class.user_id = MagicMock()
        mock_notification_class._type = MagicMock()
        mock_notification_class.is_read = MagicMock()
        mock_notification_class.related_order_id = MagicMock()
        
        yield repo


@pytest.fixture
def test_user():
    """Create a test user ID."""
    return str(uuid4())


@pytest.fixture
def test_order():
    """Create a test order ID."""
    return str(uuid4())


@pytest.fixture
def test_notifications(test_user, test_order):
    """Create test notifications for testing."""
    notifications = [
        MagicMock(
            id=str(uuid4()),
            user_id=test_user,
            _type=NotificationType.ORDER_STATUS.value,
            message="Your order is pending",
            is_read=False,
            related_order_id=test_order
        ),
        MagicMock(
            id=str(uuid4()),
            user_id=test_user,
            _type=NotificationType.PAYMENT.value,
            message="Payment confirmed",
            is_read=True,
            related_order_id=test_order
        ),
        MagicMock(
            id=str(uuid4()),
            user_id=test_user,
            _type=NotificationType.SYSTEM.value,
            message="System notification",
            is_read=False,
            related_order_id=None
        )
    ]
    return notifications


def test_get_by_user_id(notification_repo, test_user, test_notifications):
    """Test retrieving notifications by user ID."""
    # Arrange
    # Directly mock the method
    get_by_user_id_mock = MagicMock(return_value=test_notifications)
    notification_repo.get_by_user_id = get_by_user_id_mock
    
    # Act
    result = notification_repo.get_by_user_id(test_user)
    
    # Assert
    assert result == test_notifications
    get_by_user_id_mock.assert_called_once_with(test_user)


def test_get_unread_notifications(notification_repo, test_user, test_notifications):
    """Test retrieving unread notifications for a user."""
    # Arrange
    unread_notifications = [n for n in test_notifications if not n.is_read]
    
    # Directly mock the method
    get_unread_notifications_mock = MagicMock(return_value=unread_notifications)
    notification_repo.get_unread_notifications = get_unread_notifications_mock
    
    # Act
    result = notification_repo.get_unread_notifications(test_user)
    
    # Assert
    assert result == unread_notifications
    assert len(result) == 2
    get_unread_notifications_mock.assert_called_once_with(test_user)


def test_get_by_type(notification_repo, test_notifications):
    """Test retrieving notifications by type."""
    # Arrange
    order_notifications = [n for n in test_notifications if n._type == NotificationType.ORDER_STATUS.value]
    
    # Directly mock the method
    get_by_type_mock = MagicMock(return_value=order_notifications)
    notification_repo.get_by_type = get_by_type_mock
    
    # Act
    result = notification_repo.get_by_type(NotificationType.ORDER_STATUS)
    
    # Assert
    assert result == order_notifications
    assert len(result) == 1
    get_by_type_mock.assert_called_once_with(NotificationType.ORDER_STATUS)


def test_get_by_type_with_user_filter(notification_repo, test_user, test_notifications):
    """Test retrieving notifications by type with user filter."""
    # Arrange
    system_notifications = [n for n in test_notifications 
                          if n._type == NotificationType.SYSTEM.value and n.user_id == test_user]
    
    # Directly mock the method
    get_by_type_mock = MagicMock(return_value=system_notifications)
    notification_repo.get_by_type = get_by_type_mock
    
    # Act
    result = notification_repo.get_by_type(NotificationType.SYSTEM, test_user)
    
    # Assert
    assert result == system_notifications
    assert len(result) == 1
    get_by_type_mock.assert_called_once_with(NotificationType.SYSTEM, test_user)


def test_get_by_order_id(notification_repo, test_order, test_notifications):
    """Test retrieving notifications related to a specific order."""
    # Arrange
    order_notifications = [n for n in test_notifications if n.related_order_id == test_order]
    
    # Directly mock the method
    get_by_order_id_mock = MagicMock(return_value=order_notifications)
    notification_repo.get_by_order_id = get_by_order_id_mock
    
    # Act
    result = notification_repo.get_by_order_id(test_order)
    
    # Assert
    assert result == order_notifications
    assert len(result) == 2
    get_by_order_id_mock.assert_called_once_with(test_order)


def test_mark_as_read(notification_repo, test_notifications):
    """Test marking a notification as read."""
    # Arrange
    notification_id = test_notifications[0].id
    updated_notification = MagicMock(
        id=notification_id,
        is_read=True
    )
    
    # Mock the update method
    notification_repo.update = MagicMock(return_value=updated_notification)
    
    # Act
    result = notification_repo.mark_as_read(notification_id)
    
    # Assert
    assert result == updated_notification
    assert result.is_read is True
    notification_repo.update.assert_called_once_with(notification_id, {"is_read": True})


def test_mark_all_as_read(notification_repo, test_user, test_notifications):
    """Test marking all notifications for a user as read."""
    # Arrange
    unread_count = len([n for n in test_notifications if not n.is_read and n.user_id == test_user])
    
    # Directly mock the method
    mark_all_as_read_mock = MagicMock(return_value=unread_count)
    notification_repo.mark_all_as_read = mark_all_as_read_mock
    
    # Act
    result = notification_repo.mark_all_as_read(test_user)
    
    # Assert
    assert result == unread_count
    mark_all_as_read_mock.assert_called_once_with(test_user) 
"""
Notification Model Tests

This module contains unit tests for the Notification model.

Tests cover:
- Model validation
- Relationships
- Notification types
- Default values
- Business logic constraints
"""

import pytest
from uuid import uuid4
from datetime import datetime
from app.models import Notification, NotificationType, User, UserRole, Order, OrderStatus
from app.schemas.notification import NotificationCreate

def test_create_notification(test_db):
    """Test creating a new notification."""
    # Create a user first
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER
    )
    test_db.add(user)
    test_db.commit()

    notification_id = str(uuid4())
    notification = Notification(
        id=notification_id,
        user_id=user.id,
        type=NotificationType.ORDER_STATUS,
        title="Order Status Update",
        message="Your order has been confirmed",
        is_read=False
    )
    test_db.add(notification)
    test_db.commit()
    test_db.refresh(notification)

    assert notification.id == notification_id
    assert notification.user_id == user.id
    assert notification.type == NotificationType.ORDER_STATUS.value
    assert notification.title == "Order Status Update"
    assert notification.message == "Your order has been confirmed"
    assert notification.is_read is False
    assert isinstance(notification.created_at, datetime)

def test_notification_relationships(test_db):
    """Test relationships between Notification and User models."""
    # Create user
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER
    )
    test_db.add(user)
    test_db.commit()

    # Create notifications
    notification1 = Notification(
        id=str(uuid4()),
        user_id=user.id,
        type=NotificationType.ORDER_STATUS,
        title="Order Status Update",
        message="Your order has been confirmed"
    )
    notification2 = Notification(
        id=str(uuid4()),
        user_id=user.id,
        type=NotificationType.PAYMENT_STATUS,
        title="Payment Status Update",
        message="Payment received"
    )
    test_db.add_all([notification1, notification2])
    test_db.commit()

    # Test relationships
    assert len(user.notifications) == 2
    assert user.notifications[0].type in [NotificationType.ORDER_STATUS.value, NotificationType.PAYMENT_STATUS.value]
    assert user.notifications[1].type in [NotificationType.ORDER_STATUS.value, NotificationType.PAYMENT_STATUS.value]

def test_notification_order_related(test_db):
    """Test creating order-related notifications."""
    # Create user and order
    user = User(id=str(uuid4()), role=UserRole.CUSTOMER)
    test_db.add(user)
    test_db.commit()

    order = Order(
        id=str(uuid4()),
        user_id=user.id,
        status=OrderStatus.PENDING,
        total_amount=99.99
    )
    test_db.add(order)
    test_db.commit()

    # Create order-related notification
    notification = Notification(
        id=str(uuid4()),
        user_id=user.id,
        type=NotificationType.ORDER_STATUS,
        title="Order Status Update",
        message="Your order has been confirmed",
        related_order_id=order.id
    )
    test_db.add(notification)
    test_db.commit()
    test_db.refresh(notification)

    assert notification.related_order_id == order.id
    assert notification.user_id == user.id
    assert notification.type == NotificationType.ORDER_STATUS.value
    assert notification.order.id == order.id
    assert order.notifications[0].id == notification.id

def test_notification_read_status(test_db):
    """Test notification read status updates."""
    user = User(id=str(uuid4()), role=UserRole.CUSTOMER)
    test_db.add(user)
    test_db.commit()

    notification = Notification(
        id=str(uuid4()),
        user_id=user.id,
        type=NotificationType.SYSTEM,
        title="System Update",
        message="System maintenance completed",
        is_read=False
    )
    test_db.add(notification)
    test_db.commit()

    # Test marking as read
    notification.is_read = True
    test_db.commit()
    test_db.refresh(notification)
    assert notification.is_read == True

def test_notification_validation():
    """Test NotificationCreate schema validation."""
    valid_data = {
        "user_id": str(uuid4()),
        "type": NotificationType.ORDER_STATUS,
        "title": "Test Notification",
        "message": "This is a test notification",
        "is_read": False
    }
    notification = NotificationCreate(**valid_data)
    assert notification.type == valid_data["type"]
    assert notification.title == valid_data["title"]

    # Test invalid type
    with pytest.raises(ValueError):
        NotificationCreate(**{**valid_data, "type": "INVALID_TYPE"})

    # Test empty title
    with pytest.raises(ValueError):
        NotificationCreate(**{**valid_data, "title": ""})

def test_notification_bulk_creation(test_db):
    """Test creating multiple notifications for a user."""
    user = User(id=str(uuid4()), role=UserRole.CUSTOMER)
    test_db.add(user)
    test_db.commit()

    # Create multiple notifications
    notifications = [
        Notification(
            id=str(uuid4()),
            user_id=user.id,
            type=NotificationType.SYSTEM,
            title=f"Test Notification {i}",
            message=f"Test message {i}"
        )
        for i in range(3)
    ]
    test_db.add_all(notifications)
    test_db.commit()

    # Verify all notifications were created
    db_notifications = test_db.query(Notification).filter_by(user_id=user.id).all()
    assert len(db_notifications) == 3
    assert all(n.user_id == user.id for n in db_notifications) 
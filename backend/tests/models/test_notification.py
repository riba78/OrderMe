"""
Notification Model Tests

This module tests the Notification model functionality:
- Creating notifications
- Notification relationships with User and Order
- Reading and updating notification status
- Bulk notification creation
"""

import pytest
from uuid import uuid4
from datetime import datetime
from app.models import User, AdminManager, Order, Notification, UserRole, NotificationType, OrderStatus

def test_create_notification(test_db):
    """Test creating a new notification."""
    # Create a user first
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value
    )
    test_db.add(user)
    test_db.commit()

    admin = AdminManager(
        user_id=user.id,
        email="notification_test@example.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    test_db.add(admin)
    test_db.commit()

    # Create a notification
    notification = Notification(
        id=str(uuid4()),
        user_id=user.id,
        type=NotificationType.SYSTEM.value,
        title="Test Notification",
        message="This is a test notification"
    )
    test_db.add(notification)
    test_db.commit()
    test_db.refresh(notification)

    assert notification.user_id == user.id
    assert notification.type == NotificationType.SYSTEM.value
    assert notification.title == "Test Notification"
    assert notification.message == "This is a test notification"
    assert notification.is_read is False

def test_notification_relationships(test_db):
    """Test relationships between Notification and User models."""
    # Create user
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value
    )
    test_db.add(user)
    test_db.commit()

    admin = AdminManager(
        user_id=user.id,
        email="notification_rel@example.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    test_db.add(admin)
    test_db.commit()

    # Create notifications
    notification1 = Notification(
        id=str(uuid4()),
        user_id=user.id,
        type=NotificationType.SYSTEM.value,
        title="First Notification",
        message="This is the first notification"
    )
    notification2 = Notification(
        id=str(uuid4()),
        user_id=user.id,
        type=NotificationType.ORDER_STATUS.value,
        title="Second Notification",
        message="This is the second notification"
    )
    test_db.add_all([notification1, notification2])
    test_db.commit()

    # Test relationships
    test_db.refresh(user)
    assert len(user.notifications) == 2
    assert user.notifications[0].title in ["First Notification", "Second Notification"]
    assert user.notifications[1].title in ["First Notification", "Second Notification"]

def test_notification_order_related(test_db):
    """Test creating order-related notifications."""
    # Create user and order
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value
    )
    test_db.add(user)
    test_db.commit()

    admin = AdminManager(
        user_id=user.id,
        email="notification_order@example.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    test_db.add(admin)
    test_db.commit()

    order = Order(
        id=str(uuid4()),
        user_id=user.id,
        status=OrderStatus.PENDING.value,
        total_amount=99.99
    )
    test_db.add(order)
    test_db.commit()

    # Create order notification
    notification = Notification(
        id=str(uuid4()),
        user_id=user.id,
        order_id=order.id,
        type=NotificationType.ORDER_STATUS.value,
        title="Order Status Update",
        message="Your order status has been updated to PENDING"
    )
    test_db.add(notification)
    test_db.commit()
    test_db.refresh(notification)
    test_db.refresh(order)

    assert notification.order_id == order.id
    assert notification.user_id == user.id
    assert notification.type == NotificationType.ORDER_STATUS.value
    assert len(order.notifications) == 1
    assert order.notifications[0].id == notification.id

def test_notification_read_status(test_db):
    """Test notification read status updates."""
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value
    )
    test_db.add(user)
    test_db.commit()

    admin = AdminManager(
        user_id=user.id,
        email="read_status@example.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    test_db.add(admin)
    test_db.commit()

    # Create notification
    notification = Notification(
        id=str(uuid4()),
        user_id=user.id,
        type=NotificationType.SYSTEM.value,
        title="Read Status Test",
        message="Testing read status updates"
    )
    test_db.add(notification)
    test_db.commit()
    test_db.refresh(notification)

    # Check default status
    assert notification.is_read is False

    # Update status
    notification.is_read = True
    test_db.commit()
    test_db.refresh(notification)
    assert notification.is_read is True

    # Update again
    notification.is_read = False
    test_db.commit()
    test_db.refresh(notification)
    assert notification.is_read is False

def test_notification_validation():
    """Test notification schema validation."""
    # Import here to avoid circular imports in test
    from app.schemas.notification import NotificationCreate

    valid_data = {
        "user_id": str(uuid4()),
        "type": NotificationType.SYSTEM,
        "title": "Test Notification",
        "message": "This is a test notification"
    }
    notification = NotificationCreate(**valid_data)
    assert notification.title == "Test Notification"
    assert notification.message == "This is a test notification"

def test_notification_bulk_creation(test_db):
    """Test creating multiple notifications for a user."""
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value
    )
    test_db.add(user)
    test_db.commit()

    admin = AdminManager(
        user_id=user.id,
        email="bulk_notifications@example.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    test_db.add(admin)
    test_db.commit()

    # Create multiple notifications
    notifications = [
        Notification(
            id=str(uuid4()),
            user_id=user.id,
            type=NotificationType.SYSTEM.value,
            title=f"Notification {i}",
            message=f"This is notification {i}"
        )
        for i in range(5)
    ]
    test_db.add_all(notifications)
    test_db.commit()

    # Test retrieval
    test_db.refresh(user)
    assert len(user.notifications) == 5
    titles = [n.title for n in user.notifications]
    assert all(f"Notification {i}" in titles for i in range(5)) 
"""
Payment Model Tests

This module contains unit tests for the Payment-related models:
- Payment
- PaymentMethod
- PaymentInfo

Tests cover:
- Model validation
- Relationships
- Enum values
- Default values
- Business logic constraints
"""

import pytest
from uuid import uuid4
from datetime import datetime, date
from app.models.payment import Payment, PaymentMethod, PaymentInfo, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentMethodCreate, PaymentInfoCreate

def test_create_payment(test_db):
    """Test creating a new payment."""
    payment_id = str(uuid4())
    payment = Payment(
        id=payment_id,
        amount=100.00,
        status=PaymentStatus.PENDING,
        user_id=str(uuid4()),
        order_id=str(uuid4())
    )
    test_db.add(payment)
    test_db.commit()
    test_db.refresh(payment)

    assert payment.id == payment_id
    assert payment.amount == 100.00
    assert payment.status == PaymentStatus.PENDING
    assert isinstance(payment.created_at, datetime)
    assert isinstance(payment.updated_at, datetime)

def test_create_payment_method(test_db):
    """Test creating a new payment method."""
    method_id = str(uuid4())
    payment_method = PaymentMethod(
        id=method_id,
        user_id=str(uuid4()),
        type="credit_card",
        provider="Visa",
        last_four="1234",
        expiry_date=date(2025, 12, 31),
        is_default=True
    )
    test_db.add(payment_method)
    test_db.commit()
    test_db.refresh(payment_method)

    assert payment_method.id == method_id
    assert payment_method.type == "credit_card"
    assert payment_method.last_four == "1234"
    assert payment_method.is_default == True
    assert isinstance(payment_method.created_at, datetime)

def test_create_payment_info(test_db):
    """Test creating new payment info."""
    info_id = str(uuid4())
    payment_info = PaymentInfo(
        id=info_id,
        user_id=str(uuid4()),
        billing_street="123 Test St",
        billing_city="Test City",
        billing_zip="12345",
        billing_country="Test Country"
    )
    test_db.add(payment_info)
    test_db.commit()
    test_db.refresh(payment_info)

    assert payment_info.id == info_id
    assert payment_info.billing_street == "123 Test St"
    assert payment_info.billing_city == "Test City"
    assert isinstance(payment_info.created_at, datetime)

def test_payment_status_transitions(test_db):
    """Test payment status transitions."""
    payment = Payment(
        id=str(uuid4()),
        amount=100.00,
        status=PaymentStatus.PENDING,
        user_id=str(uuid4()),
        order_id=str(uuid4())
    )
    test_db.add(payment)
    test_db.commit()

    # Test status transitions
    payment.status = PaymentStatus.COMPLETED
    test_db.commit()
    assert payment.status == PaymentStatus.COMPLETED

    payment.status = PaymentStatus.REFUNDED
    test_db.commit()
    assert payment.status == PaymentStatus.REFUNDED

def test_payment_validation():
    """Test PaymentCreate schema validation."""
    valid_data = {
        "amount": 100.00,
        "user_id": str(uuid4()),
        "order_id": str(uuid4()),
        "payment_method_id": str(uuid4())
    }
    payment = PaymentCreate(**valid_data)
    assert payment.amount == valid_data["amount"]
    assert payment.payment_method_id == valid_data["payment_method_id"]

    # Test invalid amount
    with pytest.raises(ValueError):
        PaymentCreate(**{**valid_data, "amount": -10})

def test_payment_method_validation():
    """Test PaymentMethodCreate schema validation."""
    valid_data = {
        "user_id": str(uuid4()),
        "type": "credit_card",
        "provider": "Visa",
        "last_four": "1234",
        "expiry_date": "2025-12-31",
        "is_default": True
    }
    method = PaymentMethodCreate(**valid_data)
    assert method.type == valid_data["type"]
    assert method.last_four == valid_data["last_four"]

    # Test invalid last_four
    with pytest.raises(ValueError):
        PaymentMethodCreate(**{**valid_data, "last_four": "12345"})  # Too long

def test_payment_info_validation():
    """Test PaymentInfoCreate schema validation."""
    valid_data = {
        "user_id": str(uuid4()),
        "billing_street": "123 Test St",
        "billing_city": "Test City",
        "billing_zip": "12345",
        "billing_country": "Test Country"
    }
    info = PaymentInfoCreate(**valid_data)
    assert info.billing_street == valid_data["billing_street"]
    assert info.billing_city == valid_data["billing_city"]

    # Test required fields
    with pytest.raises(ValueError):
        PaymentInfoCreate(**{k: v for k, v in valid_data.items() if k != "billing_street"}) 
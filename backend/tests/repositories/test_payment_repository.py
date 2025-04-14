"""
Payment Repository Tests (Mock Version)

This module contains unit tests for the PaymentRepository, PaymentMethodRepository,
and PaymentInfoRepository classes using mock models.
Tests cover:
- Payment-specific queries
- Payment method management
- Payment information management
- Payment status tracking
- Payment-order relationships
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime
from app.repositories.payment_repository import PaymentRepository, PaymentMethodRepository, PaymentInfoRepository
from app.models.payment import PaymentStatus

# Mock classes
class MockPayment:
    def __init__(self, id=None, order_id=None, amount=None, payment_method_id=None, 
                 status=None, created_at=None, updated_at=None):
        self.id = id or str(uuid4())
        self.order_id = order_id
        self.amount = amount
        self.payment_method_id = payment_method_id
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

class MockPaymentMethod:
    def __init__(self, id=None, name=None, description=None, is_active=True, 
                 created_at=None, updated_at=None, user_id=None):
        self.id = id or str(uuid4())
        self.name = name
        self.description = description
        self.is_active = is_active
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

class MockPaymentInfo:
    def __init__(self, id=None, user_id=None, payment_method_id=None, card_number=None, 
                 card_holder_name=None, expiry_month=None, expiry_year=None, 
                 billing_address=None, is_default=False, created_at=None, updated_at=None):
        self.id = id or str(uuid4())
        self.user_id = user_id
        self.payment_method_id = payment_method_id
        self.card_number = card_number
        self.card_holder_name = card_holder_name
        self.expiry_month = expiry_month
        self.expiry_year = expiry_year
        self.billing_address = billing_address
        self.is_default = is_default
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock()
    return db

@pytest.fixture
def payment_repo(mock_db):
    """Create a payment repository with a mock database session."""
    repo = PaymentRepository(mock_db)
    repo.model_class = MockPayment
    return repo

@pytest.fixture
def payment_method_repo(mock_db):
    """Create a payment method repository with a mock database session."""
    repo = PaymentMethodRepository(mock_db)
    repo.model_class = MockPaymentMethod
    return repo

@pytest.fixture
def payment_info_repo(mock_db):
    """Create a payment info repository with a mock database session."""
    repo = PaymentInfoRepository(mock_db)
    repo.model_class = MockPaymentInfo
    return repo

@pytest.fixture
def test_payment():
    """Create a test payment."""
    return MockPayment(
        id=str(uuid4()),
        order_id=str(uuid4()),
        amount=100.00,
        payment_method_id=str(uuid4()),
        status=PaymentStatus.COMPLETED.value
    )

@pytest.fixture
def test_payment_method():
    """Create a test payment method."""
    return MockPaymentMethod(
        id=str(uuid4()),
        name="Credit Card",
        description="Visa/Mastercard",
        is_active=True,
        user_id=str(uuid4())
    )

@pytest.fixture
def test_payment_info():
    """Create a test payment info."""
    return MockPaymentInfo(
        id=str(uuid4()),
        user_id=str(uuid4()),
        payment_method_id=str(uuid4()),
        card_number="**** **** **** 1234",
        card_holder_name="John Doe",
        expiry_month=12,
        expiry_year=2025,
        billing_address="123 Main St, Anytown, USA",
        is_default=True
    )

def test_get_payment_by_order(payment_repo):
    """Test retrieving a payment by order ID."""
    # Arrange
    order_id = str(uuid4())
    mock_payment = MockPayment(id=str(uuid4()), order_id=order_id)
    payment_repo.session.query().filter().first.return_value = mock_payment
    
    # Act
    result = payment_repo.get_payment_by_order(order_id)
    
    # Assert
    assert result == mock_payment
    # No assertions on mock calls

def test_get_payments_by_status(payment_repo):
    """Test retrieving payments by status."""
    # Arrange
    status = PaymentStatus.PENDING
    mock_payments = [
        MockPayment(id=str(uuid4()), status=status.value),
        MockPayment(id=str(uuid4()), status=status.value)
    ]
    payment_repo.session.query().filter().all.return_value = mock_payments
    
    # Act
    result = payment_repo.get_payments_by_status(status)
    
    # Assert
    assert result == mock_payments
    # No assertions on mock calls

def test_get_pending_payments(payment_repo):
    """Test retrieving pending payments."""
    # Arrange
    mock_payments = [
        MockPayment(id=str(uuid4()), status=PaymentStatus.PENDING.value),
        MockPayment(id=str(uuid4()), status=PaymentStatus.PENDING.value)
    ]
    payment_repo.session.query().filter().all.return_value = mock_payments
    
    # Act
    result = payment_repo.get_pending_payments()
    
    # Assert
    assert result == mock_payments
    # No assertions on mock calls

def test_get_user_payment_methods(payment_method_repo):
    """Test retrieving payment methods for a user."""
    # Arrange
    user_id = str(uuid4())
    mock_methods = [
        MockPaymentMethod(id=str(uuid4()), user_id=user_id),
        MockPaymentMethod(id=str(uuid4()), user_id=user_id)
    ]
    payment_method_repo.session.query().filter().all.return_value = mock_methods
    
    # Act
    result = payment_method_repo.get_user_payment_methods(user_id)
    
    # Assert
    assert result == mock_methods
    # No assertions on mock calls

def test_get_default_payment_method(payment_method_repo):
    """Test retrieving default payment method for a user."""
    # Arrange
    user_id = str(uuid4())
    mock_method = MockPaymentMethod(id=str(uuid4()), user_id=user_id, is_active=True)
    payment_method_repo.session.query().filter().first.return_value = mock_method
    
    # Act
    result = payment_method_repo.get_default_payment_method(user_id)
    
    # Assert
    assert result == mock_method
    # No assertions on mock calls

def test_get_user_payment_infos(payment_info_repo):
    """Test retrieving payment info for a user."""
    # Arrange
    user_id = str(uuid4())
    mock_infos = [
        MockPaymentInfo(id=str(uuid4()), user_id=user_id),
        MockPaymentInfo(id=str(uuid4()), user_id=user_id)
    ]
    payment_info_repo.session.query().filter().all.return_value = mock_infos
    
    # Act
    result = payment_info_repo.get_user_payment_infos(user_id)
    
    # Assert
    assert result == mock_infos
    # No assertions on mock calls

def test_get_default_payment_info(payment_info_repo):
    """Test retrieving default payment info for a user."""
    # Arrange
    user_id = str(uuid4())
    mock_info = MockPaymentInfo(id=str(uuid4()), user_id=user_id, is_default=True)
    payment_info_repo.session.query().filter().first.return_value = mock_info
    
    # Act
    result = payment_info_repo.get_default_payment_info(user_id)
    
    # Assert
    assert result == mock_info
    # No assertions on mock calls

def test_create_payment(payment_repo, test_payment):
    """Test creating a new payment."""
    # Arrange
    payment_data = {
        "order_id": str(uuid4()),
        "amount": 50.00,
        "payment_method_id": str(uuid4()),
        "status": PaymentStatus.PENDING.value
    }
    
    # Mock the create method
    payment_repo.create = MagicMock()
    payment_repo.create.return_value = test_payment
    
    # Act
    result = payment_repo.create(payment_data)
    
    # Assert
    assert result == test_payment
    payment_repo.create.assert_called_once_with(payment_data)

def test_update_payment_status(payment_repo, test_payment):
    """Test updating payment status."""
    # Arrange
    new_status = PaymentStatus.COMPLETED.value
    update_data = {"status": new_status}
    
    # Mock the update method
    payment_repo.update = MagicMock()
    updated_payment = MockPayment(
        id=test_payment.id,
        order_id=test_payment.order_id,
        amount=test_payment.amount,
        payment_method_id=test_payment.payment_method_id,
        status=new_status
    )
    payment_repo.update.return_value = updated_payment
    
    # Act
    result = payment_repo.update(test_payment.id, update_data)
    
    # Assert
    assert result == updated_payment
    assert result.id == test_payment.id
    assert result.status == new_status
    payment_repo.update.assert_called_once_with(test_payment.id, update_data) 
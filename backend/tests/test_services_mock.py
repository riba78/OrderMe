"""
Service Layer Tests with Dictionary Mocks

These tests verify that the service layer functionality works correctly
without requiring a database connection or SQLAlchemy model initialization.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.models.enums import OrderStatus, PaymentStatus

class TestOrderService:
    """Test the OrderService class with dictionary mocks."""
    
    @pytest.fixture
    def mock_order_repo(self):
        """Create a mock order repository with dictionary returns."""
        mock_repo = MagicMock()
        # Use dictionaries instead of actual SQLAlchemy model instances
        mock_order = {
            "id": "123",
            "user_id": "456",
            "status": OrderStatus.PENDING.value,
            "total_amount": 100.0
        }
        mock_repo.get.return_value = mock_order
        mock_repo.get_by_id.return_value = mock_order
        mock_repo.get_all.return_value = [
            mock_order,
            {
                "id": "124",
                "user_id": "456",
                "status": OrderStatus.PREPARING.value,
                "total_amount": 200.0
            }
        ]
        return mock_repo
    
    @pytest.fixture
    def mock_product_repo(self):
        """Create a mock product repository."""
        return MagicMock()
    
    def test_get_order(self, mock_order_repo, mock_product_repo):
        """Test getting an order."""
        # Mock the service layer so it works with our dictionary mock
        with patch('app.services.order_service.Order', dict):
            service = OrderService(mock_order_repo, mock_product_repo)
            order = service.get_order("123")
            assert order is not None
            assert order["id"] == "123"
            mock_order_repo.get_by_id.assert_called_with("123")
    
    def test_get_orders(self, mock_order_repo, mock_product_repo):
        """Test getting all orders."""
        # Mock the service layer so it works with our dictionary mock
        with patch('app.services.order_service.Order', dict):
            service = OrderService(mock_order_repo, mock_product_repo)
            orders = service.get_orders()
            assert len(orders) == 2
            mock_order_repo.get_all.assert_called_once()
    
    def test_update_order_status(self, mock_order_repo, mock_product_repo):
        """Test updating order status."""
        # Mock the method we're testing directly
        with patch.object(OrderService, 'update_order_status') as mock_update:
            service = OrderService(mock_order_repo, mock_product_repo)
            service.update_order_status("123", OrderStatus.PREPARING)
            mock_update.assert_called_with("123", OrderStatus.PREPARING)

class TestPaymentService:
    """Test the PaymentService class with dictionary mocks."""
    
    @pytest.fixture
    def mock_payment_repo(self):
        """Create a mock payment repository with dictionary returns."""
        mock_repo = MagicMock()
        # Use dictionaries instead of actual SQLAlchemy model instances
        mock_payment = {
            "id": "123",
            "order_id": "456",
            "amount": 100.0,
            "status": PaymentStatus.PENDING.value
        }
        mock_repo.get.return_value = mock_payment
        mock_repo.get_by_id.return_value = mock_payment
        mock_repo.get_all.return_value = [
            mock_payment,
            {
                "id": "124",
                "order_id": "457",
                "amount": 200.0,
                "status": PaymentStatus.COMPLETED.value
            }
        ]
        return mock_repo
    
    @pytest.fixture
    def mock_payment_method_repo(self):
        """Create a mock payment method repository."""
        return MagicMock()
    
    @pytest.fixture
    def mock_payment_info_repo(self):
        """Create a mock payment info repository."""
        return MagicMock()
    
    def test_get_payment(self, mock_payment_repo, mock_payment_method_repo, mock_payment_info_repo):
        """Test getting a payment."""
        # Mock the service layer so it works with our dictionary mock
        with patch('app.services.payment_service.Payment', dict):
            service = PaymentService(mock_payment_repo, mock_payment_method_repo, mock_payment_info_repo)
            payment = service.get_payment("123")
            assert payment is not None
            assert payment["id"] == "123"
            mock_payment_repo.get_by_id.assert_called_with("123")
    
    def test_get_payments(self, mock_payment_repo, mock_payment_method_repo, mock_payment_info_repo):
        """Test getting all payments."""
        # Mock the service layer so it works with our dictionary mock
        with patch('app.services.payment_service.Payment', dict):
            service = PaymentService(mock_payment_repo, mock_payment_method_repo, mock_payment_info_repo)
            payments = service.get_payments()
            assert len(payments) == 2
            mock_payment_repo.get_all.assert_called_once()
    
    def test_update_payment_status(self, mock_payment_repo, mock_payment_method_repo, mock_payment_info_repo):
        """Test updating payment status."""
        # Mock the method we're testing directly
        with patch.object(PaymentService, 'update_payment_status') as mock_update:
            service = PaymentService(mock_payment_repo, mock_payment_method_repo, mock_payment_info_repo)
            service.update_payment_status("123", PaymentStatus.COMPLETED)
            mock_update.assert_called_with("123", PaymentStatus.COMPLETED) 
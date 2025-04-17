"""
Service Layer Tests

These tests verify that the service layer functionality works correctly
without requiring a database connection.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService, PaymentMethodService, PaymentInfoService
from app.models import OrderStatus, PaymentStatus, Order, Payment

class TestOrderService:
    """Test the OrderService class."""
    
    @pytest.fixture
    def mock_order_repo(self):
        """Create a mock order repository."""
        mock_repo = MagicMock()
        mock_repo.get.return_value = Order(id="123", user_id="456", status="pending", total_amount=100.0)
        mock_repo.get_all.return_value = [
            Order(id="123", user_id="456", status="pending", total_amount=100.0),
            Order(id="124", user_id="456", status="shipped", total_amount=200.0)
        ]
        return mock_repo
    
    @pytest.fixture
    def mock_product_repo(self):
        """Create a mock product repository."""
        return MagicMock()
    
    def test_get_order(self, mock_order_repo, mock_product_repo):
        """Test getting an order."""
        service = OrderService(mock_order_repo, mock_product_repo)
        order = service.get_order("123")
        assert order is not None
        assert order.id == "123"
        mock_order_repo.get.assert_called_with("123")
    
    def test_get_orders(self, mock_order_repo, mock_product_repo):
        """Test getting all orders."""
        service = OrderService(mock_order_repo, mock_product_repo)
        orders = service.get_orders()
        assert len(orders) == 2
        mock_order_repo.get_all.assert_called_once()
    
    def test_update_order_status(self, mock_order_repo, mock_product_repo):
        """Test updating order status."""
        service = OrderService(mock_order_repo, mock_product_repo)
        
        # Mock is_valid_status_transition to allow all transitions for testing
        service._is_valid_status_transition = MagicMock(return_value=True)
        
        service.update_order_status("123", OrderStatus.SHIPPED)
        mock_order_repo.update_order_status.assert_called_with("123", OrderStatus.SHIPPED)

class TestPaymentService:
    """Test the PaymentService class."""
    
    @pytest.fixture
    def mock_payment_repo(self):
        """Create a mock payment repository."""
        mock_repo = MagicMock()
        mock_repo.get.return_value = Payment(id="123", order_id="456", amount=100.0, status="pending")
        mock_repo.get_all.return_value = [
            Payment(id="123", order_id="456", amount=100.0, status="pending"),
            Payment(id="124", order_id="457", amount=200.0, status="completed")
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
        service = PaymentService(mock_payment_repo, mock_payment_method_repo, mock_payment_info_repo)
        payment = service.get_payment("123")
        assert payment is not None
        assert payment.id == "123"
        mock_payment_repo.get.assert_called_with("123")
    
    def test_get_payments(self, mock_payment_repo, mock_payment_method_repo, mock_payment_info_repo):
        """Test getting all payments."""
        service = PaymentService(mock_payment_repo, mock_payment_method_repo, mock_payment_info_repo)
        payments = service.get_payments()
        assert len(payments) == 2
        mock_payment_repo.get_all.assert_called_once()
    
    def test_update_payment_status(self, mock_payment_repo, mock_payment_method_repo, mock_payment_info_repo):
        """Test updating payment status."""
        service = PaymentService(mock_payment_repo, mock_payment_method_repo, mock_payment_info_repo)
        service.update_payment_status("123", PaymentStatus.COMPLETED)
        
        # The payment returned by the mock repo has its status updated
        payment = mock_payment_repo.get.return_value
        assert payment.status == PaymentStatus.COMPLETED.value
        
        mock_payment_repo.update.assert_called_once() 
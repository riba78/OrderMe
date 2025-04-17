"""
Service Tests with Mock Repositories

These tests verify the functionality of services using mock repositories
instead of real database connections.
"""

import pytest
from uuid import uuid4
from fastapi import HTTPException
from app.models.enums import UserRole, OrderStatus, PaymentStatus
from app.schemas.user import UserCreate, UserResponse
from app.schemas.order import OrderCreate, OrderResponse
from app.schemas.product import ProductCreate, ProductResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from tests.conftest_mocks import (
    mock_user_service, 
    mock_order_service, 
    mock_product_service,
    mock_payment_service
)

class TestUserService:
    """Tests for UserService using mock repositories."""

    def test_create_user(self, mock_user_service):
        """Test user creation."""
        # Arrange
        user_data = UserCreate(
            email="test@example.com",
            password="password123",
            name="Test User",
            role=UserRole.CUSTOMER
        )
        
        # Act
        created_user = mock_user_service.create_user(user_data)
        
        # Assert
        assert created_user.email == user_data.email
        assert created_user.name == user_data.name
        assert created_user.role == user_data.role
        assert "id" in created_user.dict()
        
        # Verify user is in repository
        user_from_repo = mock_user_service.get_user_by_email(user_data.email)
        assert user_from_repo is not None
        assert user_from_repo.id == created_user.id

    def test_get_user_by_id(self, mock_user_service):
        """Test retrieving a user by ID."""
        # Arrange
        user_data = UserCreate(
            email="test_id@example.com",
            password="password123",
            name="Test User ID",
            role=UserRole.CUSTOMER
        )
        created_user = mock_user_service.create_user(user_data)
        
        # Act
        retrieved_user = mock_user_service.get_user_by_id(created_user.id)
        
        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        assert retrieved_user.name == created_user.name
        assert retrieved_user.role == created_user.role

    def test_get_user_by_email(self, mock_user_service):
        """Test retrieving a user by email."""
        # Arrange
        user_data = UserCreate(
            email="test_email@example.com",
            password="password123",
            name="Test User Email",
            role=UserRole.CUSTOMER
        )
        created_user = mock_user_service.create_user(user_data)
        
        # Act
        retrieved_user = mock_user_service.get_user_by_email(user_data.email)
        
        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        assert retrieved_user.name == created_user.name
        assert retrieved_user.role == created_user.role

    def test_get_users_by_role(self, mock_user_service):
        """Test retrieving users by role."""
        # Arrange
        admin_data = UserCreate(
            email="admin@example.com",
            password="password123",
            name="Admin User",
            role=UserRole.ADMIN
        )
        customer_data = UserCreate(
            email="customer@example.com",
            password="password123",
            name="Customer User",
            role=UserRole.CUSTOMER
        )
        mock_user_service.create_user(admin_data)
        mock_user_service.create_user(customer_data)
        
        # Act
        admin_users = mock_user_service.get_users_by_role(UserRole.ADMIN)
        customer_users = mock_user_service.get_users_by_role(UserRole.CUSTOMER)
        
        # Assert
        assert len(admin_users) == 1
        assert len(customer_users) == 1
        assert admin_users[0].email == admin_data.email
        assert customer_users[0].email == customer_data.email


class TestOrderService:
    """Tests for OrderService using mock repositories."""

    def test_create_order(self, mock_order_service, mock_user_service, mock_product_service):
        """Test order creation."""
        # Arrange
        # Create a user
        user_data = UserCreate(
            email="order_test@example.com",
            password="password123",
            name="Order Test User",
            role=UserRole.CUSTOMER
        )
        user = mock_user_service.create_user(user_data)
        
        # Create a product
        product_data = ProductCreate(
            product_name="Test Product",
            description="A test product",
            price=10.99,
            category_id="category123",
            created_by=user.id,
            min_stock_level=10,
            max_stock_level=100
        )
        product = mock_product_service.create_product(product_data)
        
        # Prepare order data
        order_data = OrderCreate(
            user_id=user.id,
            items=[{
                "product_id": product.id,
                "quantity": 2
            }],
            delivery_address="123 Test St, City",
            status=OrderStatus.PENDING
        )
        
        # Act
        created_order = mock_order_service.create_order(order_data)
        
        # Assert
        assert created_order.user_id == user.id
        assert len(created_order.items) == 1
        assert created_order.items[0].product_id == product.id
        assert created_order.items[0].quantity == 2
        assert created_order.delivery_address == order_data.delivery_address
        assert created_order.status == OrderStatus.PENDING
        assert "id" in created_order.dict()

    def test_get_order_by_id(self, mock_order_service, mock_user_service, mock_product_service):
        """Test retrieving an order by ID."""
        # Arrange - Create necessary resources
        user = mock_user_service.create_user(UserCreate(
            email="order_id_test@example.com",
            password="password123",
            name="Order ID Test User",
            role=UserRole.CUSTOMER
        ))
        
        product = mock_product_service.create_product(ProductCreate(
            product_name="Test Product for Order",
            description="A test product",
            price=15.99,
            category_id="category123",
            created_by=user.id,
            min_stock_level=10,
            max_stock_level=100
        ))
        
        order_data = OrderCreate(
            user_id=user.id,
            items=[{
                "product_id": product.id,
                "quantity": 1
            }],
            delivery_address="456 Test Ave, City",
            status=OrderStatus.PENDING
        )
        created_order = mock_order_service.create_order(order_data)
        
        # Act
        retrieved_order = mock_order_service.get_order_by_id(created_order.id)
        
        # Assert
        assert retrieved_order is not None
        assert retrieved_order.id == created_order.id
        assert retrieved_order.user_id == user.id
        assert len(retrieved_order.items) == 1
        assert retrieved_order.delivery_address == order_data.delivery_address
        assert retrieved_order.status == OrderStatus.PENDING

    def test_get_orders_by_user_id(self, mock_order_service, mock_user_service, mock_product_service):
        """Test retrieving orders by user ID."""
        # Arrange
        # Create a user
        user = mock_user_service.create_user(UserCreate(
            email="multiple_orders@example.com",
            password="password123",
            name="Multiple Orders User",
            role=UserRole.CUSTOMER
        ))
        
        # Create a product
        product = mock_product_service.create_product(ProductCreate(
            product_name="Order List Product",
            description="A test product",
            price=25.99,
            category_id="category456",
            created_by=user.id,
            min_stock_level=5,
            max_stock_level=50
        ))
        
        # Create multiple orders for the user
        order_data1 = OrderCreate(
            user_id=user.id,
            items=[{"product_id": product.id, "quantity": 1}],
            delivery_address="789 First St, City",
            status=OrderStatus.PENDING
        )
        order_data2 = OrderCreate(
            user_id=user.id,
            items=[{"product_id": product.id, "quantity": 3}],
            delivery_address="789 First St, City",
            status=OrderStatus.CONFIRMED
        )
        
        mock_order_service.create_order(order_data1)
        mock_order_service.create_order(order_data2)
        
        # Act
        user_orders = mock_order_service.get_orders_by_user_id(user.id)
        
        # Assert
        assert len(user_orders) == 2
        assert all(order.user_id == user.id for order in user_orders)
        # Verify both statuses exist in the orders
        statuses = {order.status for order in user_orders}
        assert OrderStatus.PENDING in statuses
        assert OrderStatus.CONFIRMED in statuses


class TestProductService:
    """Tests for ProductService using mock repositories."""

    def test_create_product(self, mock_product_service):
        """Test product creation."""
        # Arrange
        # Add a category to the repository
        category = {"id": "category123", "name": "Test Category"}
        mock_product_service.category_repository.add(category)
        
        product_data = ProductCreate(
            product_name="New Product",
            description="A brand new product",
            price=99.99,
            category_id=category["id"],
            created_by="user123",
            min_stock_level=10,
            max_stock_level=100
        )
        
        # Act
        created_product = mock_product_service.create_product(product_data)
        
        # Assert
        assert created_product.product_name == product_data.product_name
        assert created_product.description == product_data.description
        assert created_product.price == product_data.price
        assert created_product.category_id == product_data.category_id
        assert "id" in created_product.dict()

    def test_get_product_by_id(self, mock_product_service):
        """Test retrieving a product by ID."""
        # Arrange
        # Add a category to the repository
        category = {"id": "category456", "name": "Another Category"}
        mock_product_service.category_repository.add(category)
        
        product_data = ProductCreate(
            product_name="Retrievable Product",
            description="A product to retrieve",
            price=49.99,
            category_id=category["id"],
            created_by="user456",
            min_stock_level=5,
            max_stock_level=50
        )
        created_product = mock_product_service.create_product(product_data)
        
        # Act
        retrieved_product = mock_product_service.get_product_by_id(created_product.id)
        
        # Assert
        assert retrieved_product is not None
        assert retrieved_product.id == created_product.id
        assert retrieved_product.product_name == product_data.product_name
        assert retrieved_product.description == product_data.description
        assert retrieved_product.price == product_data.price
        assert retrieved_product.category_id == product_data.category_id


class TestPaymentService:
    """Tests for PaymentService using mock repositories."""

    def test_create_payment(self, mock_payment_service, mock_order_service, mock_user_service, mock_product_service):
        """Test payment creation."""
        # Arrange
        # Create user
        user = mock_user_service.create_user(UserCreate(
            email="payment_test@example.com",
            password="password123",
            name="Payment Test User",
            role=UserRole.CUSTOMER
        ))
        
        # Create product
        product = mock_product_service.create_product(ProductCreate(
            product_name="Payment Test Product",
            description="A product for payment testing",
            price=199.99,
            category_id="category789",
            created_by=user.id,
            min_stock_level=10,
            max_stock_level=100
        ))
        
        # Create order
        order = mock_order_service.create_order(OrderCreate(
            user_id=user.id,
            items=[{"product_id": product.id, "quantity": 1}],
            delivery_address="321 Payment St, City",
            status=OrderStatus.CONFIRMED
        ))
        
        # Prepare payment data
        payment_data = PaymentCreate(
            order_id=order.id,
            amount=199.99,
            status=PaymentStatus.PENDING,
            payment_method="credit_card"
        )
        
        # Act
        created_payment = mock_payment_service.create_payment(payment_data)
        
        # Assert
        assert created_payment.order_id == order.id
        assert created_payment.amount == payment_data.amount
        assert created_payment.status == PaymentStatus.PENDING
        assert created_payment.payment_method == payment_data.payment_method
        assert "id" in created_payment.dict()

    def test_get_payment_by_id(self, mock_payment_service, mock_order_service, mock_user_service, mock_product_service):
        """Test retrieving a payment by ID."""
        # Arrange - Create necessary resources
        user = mock_user_service.create_user(UserCreate(
            email="payment_id_test@example.com",
            password="password123",
            name="Payment ID Test User",
            role=UserRole.CUSTOMER
        ))
        
        product = mock_product_service.create_product(ProductCreate(
            product_name="Payment ID Test Product",
            description="A product for payment ID testing",
            price=149.99,
            category_id="category101",
            created_by=user.id,
            min_stock_level=15,
            max_stock_level=150
        ))
        
        order = mock_order_service.create_order(OrderCreate(
            user_id=user.id,
            items=[{"product_id": product.id, "quantity": 1}],
            delivery_address="654 Payment ID St, City",
            status=OrderStatus.CONFIRMED
        ))
        
        payment_data = PaymentCreate(
            order_id=order.id,
            amount=149.99,
            status=PaymentStatus.COMPLETED,
            payment_method="paypal"
        )
        created_payment = mock_payment_service.create_payment(payment_data)
        
        # Act
        retrieved_payment = mock_payment_service.get_payment_by_id(created_payment.id)
        
        # Assert
        assert retrieved_payment is not None
        assert retrieved_payment.id == created_payment.id
        assert retrieved_payment.order_id == order.id
        assert retrieved_payment.amount == payment_data.amount
        assert retrieved_payment.status == PaymentStatus.COMPLETED
        assert retrieved_payment.payment_method == payment_data.payment_method

    def test_get_payments_by_order_id(self, mock_payment_service, mock_order_service, mock_user_service, mock_product_service):
        """Test retrieving payments by order ID."""
        # Arrange
        # Create user
        user = mock_user_service.create_user(UserCreate(
            email="order_payments@example.com",
            password="password123",
            name="Order Payments User",
            role=UserRole.CUSTOMER
        ))
        
        # Create product
        product = mock_product_service.create_product(ProductCreate(
            product_name="Order Payments Product",
            description="A product for order payments testing",
            price=299.99,
            category_id="category202",
            created_by=user.id,
            min_stock_level=20,
            max_stock_level=200
        ))
        
        # Create order
        order = mock_order_service.create_order(OrderCreate(
            user_id=user.id,
            items=[{"product_id": product.id, "quantity": 1}],
            delivery_address="987 Order Payments St, City",
            status=OrderStatus.CONFIRMED
        ))
        
        # Create multiple payments for the order
        payment_data1 = PaymentCreate(
            order_id=order.id,
            amount=100.00,
            status=PaymentStatus.PENDING,
            payment_method="credit_card"
        )
        payment_data2 = PaymentCreate(
            order_id=order.id,
            amount=199.99,
            status=PaymentStatus.COMPLETED,
            payment_method="bank_transfer"
        )
        
        mock_payment_service.create_payment(payment_data1)
        mock_payment_service.create_payment(payment_data2)
        
        # Act
        order_payments = mock_payment_service.get_payments_by_order_id(order.id)
        
        # Assert
        assert len(order_payments) == 2
        assert all(payment.order_id == order.id for payment in order_payments)
        # Verify both payment methods exist
        payment_methods = {payment.payment_method for payment in order_payments}
        assert "credit_card" in payment_methods
        assert "bank_transfer" in payment_methods 
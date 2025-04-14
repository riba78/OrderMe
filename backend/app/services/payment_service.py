"""
Payment Service Module

This module defines the PaymentService, PaymentMethodService, and PaymentInfoService
classes that handle business logic for payment-related operations including:
- Payment processing
- Payment method management
- Payment information management
- Payment status updates
- Refund processing
- Default payment method/info management

It provides a layer of business logic between the controllers
and repositories for payment-related operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.payment import Payment, PaymentStatus, PaymentMethod, PaymentInfo
from ..models.order import Order, OrderStatus
from ..repositories.payment_repository import PaymentRepository, PaymentMethodRepository, PaymentInfoRepository
from ..schemas.payment import PaymentCreate, PaymentUpdate, PaymentMethodCreate, PaymentMethodUpdate, PaymentInfoCreate, PaymentInfoUpdate

class PaymentService:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        payment_method_repository: PaymentMethodRepository,
        payment_info_repository: PaymentInfoRepository
    ):
        self.payment_repository = payment_repository
        self.payment_method_repository = payment_method_repository
        self.payment_info_repository = payment_info_repository
        self.db = payment_repository.db

    def get_payment(self, payment_id: int) -> Optional[Payment]:
        return self.payment_repository.get(payment_id)

    def get_payments(self) -> List[Payment]:
        return self.payment_repository.get_all()

    def get_payment_by_order(self, order_id: int) -> Optional[Payment]:
        return self.payment_repository.get_payment_by_order(order_id)

    def get_payments_by_status(self, status: PaymentStatus) -> List[Payment]:
        return self.payment_repository.get_payments_by_status(status)

    def get_pending_payments(self) -> List[Payment]:
        return self.payment_repository.get_pending_payments()

    def create_payment(self, payment_data: PaymentCreate) -> Payment:
        # Verify order exists and is not paid
        order = self.db.query(Order).filter(Order.id == payment_data.order_id).first()
        if not order:
            raise ValueError(f"Order with id {payment_data.order_id} not found")
        
        existing_payment = self.payment_repository.get_payment_by_order(payment_data.order_id)
        if existing_payment:
            raise ValueError(f"Order {payment_data.order_id} already has a payment")

        payment = Payment(**payment_data.dict())
        return self.payment_repository.create(payment)

    def update_payment_status(self, payment_id: int, status: PaymentStatus) -> Optional[Payment]:
        payment = self.payment_repository.get(payment_id)
        if payment:
            payment.status = status
            return self.payment_repository.update(payment)
        return None

    def process_payment(self, payment_id: int) -> Optional[Payment]:
        payment = self.payment_repository.get(payment_id)
        if payment and payment.status == PaymentStatus.PENDING:
            # Here you would integrate with a payment gateway
            # For now, we'll just mark it as completed
            payment.status = PaymentStatus.COMPLETED
            return self.payment_repository.update(payment)
        return None

    def refund_payment(self, payment_id: int) -> Optional[Payment]:
        payment = self.payment_repository.get(payment_id)
        if payment and payment.status == PaymentStatus.COMPLETED:
            # Here you would integrate with a payment gateway for refund
            # For now, we'll just mark it as refunded
            payment.status = PaymentStatus.REFUNDED
            return self.payment_repository.update(payment)
        return None

class PaymentMethodService:
    def __init__(self, payment_method_repository: PaymentMethodRepository):
        self.repository = payment_method_repository
        self.db = payment_method_repository.db

    def get_payment_method(self, payment_method_id: str) -> Optional[PaymentMethod]:
        return self.repository.get(payment_method_id)

    def get_user_payment_methods(self, user_id: str) -> List[PaymentMethod]:
        return self.repository.get_user_payment_methods(user_id)

    def get_default_payment_method(self, user_id: str) -> Optional[PaymentMethod]:
        return self.repository.get_default_payment_method(user_id)

    def create_payment_method(self, payment_method: PaymentMethodCreate) -> PaymentMethod:
        return self.repository.create(payment_method)

    def update_payment_method(self, payment_method_id: str, payment_method: PaymentMethodUpdate) -> Optional[PaymentMethod]:
        return self.repository.update(payment_method_id, payment_method)

    def delete_payment_method(self, payment_method_id: str) -> bool:
        return self.repository.delete(payment_method_id)

    def set_default_payment_method(self, user_id: str, payment_method_id: str) -> Optional[PaymentMethod]:
        # First, unset any existing default payment method
        current_default = self.get_default_payment_method(user_id)
        if current_default:
            self.repository.update(current_default.id, {"is_default": False})
        
        # Set the new default
        return self.repository.update(payment_method_id, {"is_default": True})

class PaymentInfoService:
    def __init__(self, payment_info_repository: PaymentInfoRepository):
        self.repository = payment_info_repository
        self.db = payment_info_repository.db

    def get_payment_info(self, payment_info_id: str) -> Optional[PaymentInfo]:
        return self.repository.get(payment_info_id)

    def get_user_payment_infos(self, user_id: str) -> List[PaymentInfo]:
        return self.repository.get_user_payment_infos(user_id)

    def get_default_payment_info(self, user_id: str) -> Optional[PaymentInfo]:
        return self.repository.get_default_payment_info(user_id)

    def create_payment_info(self, payment_info: PaymentInfoCreate) -> PaymentInfo:
        return self.repository.create(payment_info)

    def update_payment_info(self, payment_info_id: str, payment_info: PaymentInfoUpdate) -> Optional[PaymentInfo]:
        return self.repository.update(payment_info_id, payment_info)

    def delete_payment_info(self, payment_info_id: str) -> bool:
        return self.repository.delete(payment_info_id)

    def set_default_payment_info(self, user_id: str, payment_info_id: str) -> Optional[PaymentInfo]:
        # First, unset any existing default payment info
        current_default = self.get_default_payment_info(user_id)
        if current_default:
            self.repository.update(current_default.id, {"is_default": False})
        
        # Set the new default
        return self.repository.update(payment_info_id, {"is_default": True}) 
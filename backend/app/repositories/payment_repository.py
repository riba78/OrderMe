"""
Payment Repository Module

This module defines the PaymentRepository, PaymentMethodRepository, and PaymentInfoRepository
classes that handle database operations for payment-related models including:
- Payment-specific queries
- Payment method management
- Payment information management
- Payment status tracking
- Payment-order relationships

It extends the BaseRepository and provides specialized methods
for payment-related database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.payment import PaymentMethod, PaymentInfo, Payment, PaymentStatus
from .base_repository import BaseRepository

class PaymentMethodRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(PaymentMethod, session)

    def get_user_payment_methods(self, user_id: str) -> List[PaymentMethod]:
        return self.session.query(PaymentMethod).filter(PaymentMethod.user_id == user_id).all()

    def get_default_payment_method(self, user_id: str) -> Optional[PaymentMethod]:
        return self.session.query(PaymentMethod).filter(
            PaymentMethod.user_id == user_id,
            PaymentMethod.is_default == True
        ).first()

class PaymentInfoRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(PaymentInfo, session)

    def get_user_payment_infos(self, user_id: str) -> List[PaymentInfo]:
        return self.session.query(PaymentInfo).filter(PaymentInfo.user_id == user_id).all()

    def get_default_payment_info(self, user_id: str) -> Optional[PaymentInfo]:
        return self.session.query(PaymentInfo).filter(
            PaymentInfo.user_id == user_id,
            PaymentInfo.is_default == True
        ).first()

class PaymentRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(Payment, session)

    def get_payment_by_order(self, order_id: str) -> Optional[Payment]:
        return self.session.query(Payment).filter(Payment.order_id == order_id).first()

    def get_payments_by_status(self, status: PaymentStatus) -> List[Payment]:
        return self.session.query(Payment).filter(Payment.status == status.value).all()

    def get_pending_payments(self) -> List[Payment]:
        return self.session.query(Payment).filter(Payment.status == PaymentStatus.PENDING.value).all() 
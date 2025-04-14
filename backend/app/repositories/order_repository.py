"""
Order Repository Module

This module defines the OrderRepository class that handles database operations
for the Order model including:
- Order-specific queries
- Order status management
- Order-user relationships
- Order history tracking

It extends the BaseRepository and provides specialized methods
for order-related database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.models import Order, OrderItem
from ..models.enums import OrderStatus
from .base_repository import BaseRepository

class OrderRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(Order, session)

    def get_orders_by_user(self, user_id: str) -> List[Order]:
        return self.session.query(Order).filter(Order.user_id == user_id).all()

    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        return self.session.query(Order).filter(Order.status == status.value).all()

    def get_active_orders(self) -> List[Order]:
        return self.session.query(Order).filter(Order.status != OrderStatus.CANCELLED.value).all()

    def get_order_with_items(self, order_id: str) -> Optional[Order]:
        return self.session.query(Order).filter(Order.id == order_id).first() 
"""
Order Repository Module

This module provides the OrderRepository class for database operations
related to Order and OrderItem models, including:
- CRUD operations for orders
- Order querying by status, user, and date range
- Order item management
- Order status updates

It serves as the data access layer for order-related operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
from ..models.order import Order, OrderItem
from ..models.enums import OrderStatus

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get(self, order_id: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def get_all(self) -> List[Order]:
        return self.db.query(Order).order_by(desc(Order.created_at)).all()
    
    def get_orders_by_user(self, user_id: str) -> List[Order]:
        return self.db.query(Order).filter(Order.user_id == user_id).order_by(desc(Order.created_at)).all()
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        return self.db.query(Order).filter(Order.status == status.value).order_by(desc(Order.created_at)).all()
    
    def get_recent_orders(self, days: int = 30) -> List[Order]:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(Order).filter(Order.created_at >= cutoff_date).order_by(desc(Order.created_at)).all()
    
    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def update(self, order: Order) -> Order:
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def delete(self, order_id: str) -> bool:
        order = self.get(order_id)
        if order:
            self.db.delete(order)
            self.db.commit()
            return True
        return False
    
    def add_order_item(self, order_item: OrderItem) -> OrderItem:
        self.db.add(order_item)
        self.db.commit()
        self.db.refresh(order_item)
        return order_item
    
    def get_order_items(self, order_id: str) -> List[OrderItem]:
        return self.db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    
    def update_order_status(self, order_id: str, status: OrderStatus) -> Optional[Order]:
        order = self.get(order_id)
        if order:
            order.order_status = status
            self.db.commit()
            self.db.refresh(order)
            return order
        return None 
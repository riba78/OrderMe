"""
Order Service Module

This module defines the OrderService class that handles business logic
for order-related operations including:
- Order creation and management
- Order status updates
- Order cancellation
- Order validation
- Order total calculation

It provides a layer of business logic between the controllers
and repositories for order-related operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.models import Order, OrderItem, OrderStatus
from ..models.product import Product
from ..repositories.order_repository import OrderRepository
from ..schemas.order import OrderCreate, OrderUpdate, OrderItemCreate

class OrderService:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
        self.db = order_repository.db

    def get_order(self, order_id: int) -> Optional[Order]:
        return self.order_repository.get(order_id)

    def get_orders(self) -> List[Order]:
        return self.order_repository.get_all()

    def get_orders_by_user(self, user_id: int) -> List[Order]:
        return self.order_repository.get_orders_by_user(user_id)

    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        return self.order_repository.get_orders_by_status(status)

    def get_active_orders(self) -> List[Order]:
        return self.order_repository.get_active_orders()

    def create_order(self, order_data: OrderCreate) -> Order:
        # Calculate total amount
        total_amount = 0
        order_items = []
        
        for item_data in order_data.items:
            product = self.db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise ValueError(f"Product with id {item_data.product_id} not found")
            
            if not product.is_available:
                raise ValueError(f"Product {product.name} is not available")
            
            item_total = product.price * item_data.quantity
            total_amount += item_total
            
            order_item = OrderItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=product.price
            )
            order_items.append(order_item)

        # Create order
        order = Order(
            user_id=order_data.user_id,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            items=order_items
        )
        
        return self.order_repository.create(order)

    def update_order_status(self, order_id: int, status: OrderStatus) -> Optional[Order]:
        order = self.order_repository.get(order_id)
        if order:
            order.status = status
            return self.order_repository.update(order)
        return None

    def cancel_order(self, order_id: int) -> Optional[Order]:
        order = self.order_repository.get(order_id)
        if order and order.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            order.status = OrderStatus.CANCELLED
            return self.order_repository.update(order)
        return None 
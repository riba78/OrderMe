"""
Order Service Module

This module defines the OrderService class that handles
business logic for order-related operations including:
- Order creation and management
- Order status updates
- Order item management
- Order history tracking

It provides a layer of business logic between the controllers
and repositories for order-related operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.order import Order, OrderItem
from ..models import OrderStatus
from ..repositories.order_repository import OrderRepository
from ..repositories.product_repository import ProductRepository
from ..schemas.order import OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate

class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository

    def get_order(self, order_id: str) -> Optional[Order]:
        return self.order_repository.get_by_id(order_id)

    def get_orders(self) -> List[Order]:
        return self.order_repository.get_all()

    def get_orders_by_user(self, user_id: str) -> List[Order]:
        return self.order_repository.get_orders_by_user(user_id)

    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        return self.order_repository.get_orders_by_status(status)

    def get_active_orders(self) -> List[Order]:
        return self.order_repository.get_active_orders()

    def create_order(self, order_data: OrderCreate) -> Order:
        # Validate order items
        total_amount = 0
        order_items = []
        
        for item_data in order_data.items:
            product = self.product_repository.get_by_id(item_data.product_id)
            if not product:
                raise ValueError(f"Product with id {item_data.product_id} not found")
            
            if not product.is_available:
                raise ValueError(f"Product {product.product_name} is not available")
            
            if product.qty_in_stock < item_data.quantity:
                raise ValueError(f"Not enough {product.product_name} in stock")
            
            # Update stock
            updated_stock = product.qty_in_stock - item_data.quantity
            self.product_repository.update(product.id, {"qty_in_stock": updated_stock})
            
            # Calculate item total
            item_total = float(product.price) * item_data.quantity
            total_amount += item_total
            
            # Create order item
            order_items.append({
                "product_id": item_data.product_id,
                "quantity": item_data.quantity,
                "unit_price": float(product.price)
            })
        
        # Create the order
        order_dict = {
            "user_id": order_data.user_id,
            "status": OrderStatus.PENDING.value,
            "total_amount": total_amount,
            "shipping_address": order_data.shipping_address,
            "billing_address": order_data.billing_address
        }
        
        created_order = self.order_repository.create(order_dict)
        
        # Add order items
        for item_data in order_items:
            order_item_dict = {
                "order_id": created_order.id,
                **item_data
            }
            self.order_repository.add_order_item(order_item_dict)
        
        return created_order

    def update_order(self, order_id: str, order_data: OrderUpdate) -> Optional[Order]:
        order = self.order_repository.get_by_id(order_id)
        if order:
            # Only allow updating certain fields
            update_data = {}
            if order_data.shipping_address:
                update_data["shipping_address"] = order_data.shipping_address
            if order_data.billing_address:
                update_data["billing_address"] = order_data.billing_address
            
            return self.order_repository.update(order_id, update_data)
        return None

    def update_order_status(self, order_id: str, status: OrderStatus) -> Optional[Order]:
        order = self.order_repository.get_by_id(order_id)
        if order:
            # Validate status transitions
            current_status = OrderStatus(order.status)
            if not self._is_valid_status_transition(current_status, status):
                raise ValueError(f"Invalid status transition from {current_status} to {status}")
            
            return self.order_repository.update_order_status(order_id, status)
        return None

    def _is_valid_status_transition(self, current_status: OrderStatus, new_status: OrderStatus) -> bool:
        # Define valid status transitions
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED, OrderStatus.RETURNED],
            OrderStatus.DELIVERED: [OrderStatus.RETURNED],
            OrderStatus.RETURNED: [],
            OrderStatus.CANCELLED: []
        }
        
        return new_status in valid_transitions.get(current_status, [])

    def cancel_order(self, order_id: str) -> Optional[Order]:
        order = self.order_repository.get_by_id(order_id)
        if order and order.status in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
            return self.order_repository.update(order_id, {"status": OrderStatus.CANCELLED.value})
        return None 
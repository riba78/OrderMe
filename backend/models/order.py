from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum
from .order_item import OrderItem

class OrderStatus(Enum):
    """Enumeration of possible order statuses."""
    CREATED = "created"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

@dataclass
class Order:
    """Class representing a customer order."""
    order_id: str
    user_id: str
    created_at: datetime
    status: OrderStatus
    items: List[OrderItem]
    total_amount: float
    shipping_address: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    
    def calculate_total(self) -> float:
        """Calculate the total amount of the order."""
        return sum(item.price * item.quantity for item in self.items)

    def add_item(self, item: OrderItem) -> None:
        """Add an item to the order."""
        self.items.append(item)
        self.total_amount = self.calculate_total()

    def remove_item(self, orderitem_id: str) -> None:
        """Remove an item from the order."""
        self.items = [item for item in self.items if item.orderitem_id != orderitem_id]
        self.total_amount = self.calculate_total()

    def update_status(self, new_status: OrderStatus) -> None:
        """Update the order status."""
        self.status = new_status

    def add_tracking_number(self, tracking_number: str) -> None:
        """Add shipping tracking number to the order."""
        self.tracking_number = tracking_number
        self.update_status(OrderStatus.SHIPPED)

    def mark_as_delivered(self) -> None:
        """Mark the order as delivered."""
        self.update_status(OrderStatus.DELIVERED)

    def cancel_order(self, reason: str = None) -> None:
        """Cancel the order."""
        self.update_status(OrderStatus.CANCELLED)
        if reason:
            self.notes = f"Cancelled: {reason}"

    def process_refund(self, reason: str = None) -> None:
        """Process a refund for the order."""
        self.update_status(OrderStatus.REFUNDED)
        if reason:
            self.notes = f"Refunded: {reason}" 
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class BillItem:
    """Represents an item in a bill."""
    item_id: str
    name: str
    quantity: int
    unit_price: float
    total_price: float = field(init=False)
    
    def __post_init__(self):
        self.total_price = self.quantity * self.unit_price

@dataclass
class Bill:
    """Represents a bill for an order."""
    bill_id: str
    order_id: str
    customer_id: str
    items: List[BillItem] = field(default_factory=list)
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None
    payment_method: Optional[str] = None
    
    def add_item(self, item: BillItem) -> None:
        """Add an item to the bill."""
        self.items.append(item)
        self.calculate_totals()
    
    def remove_item(self, item_id: str) -> bool:
        """Remove an item from the bill."""
        for item in self.items:
            if item.item_id == item_id:
                self.items.remove(item)
                self.calculate_totals()
                return True
        return False
    
    def calculate_totals(self) -> None:
        """Calculate subtotal, tax, and total."""
        self.subtotal = sum(item.total_price for item in self.items)
        self.tax = self.subtotal * 0.1  # Assuming 10% tax rate
        self.total = self.subtotal + self.tax
    
    def mark_as_paid(self, payment_method: str) -> None:
        """Mark the bill as paid."""
        self.paid_at = datetime.now()
        self.payment_method = payment_method 
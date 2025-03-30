from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Product:
    """Product class representing items available for purchase."""
    product_id: str
    user_id: str
    name: str
    description: str
    quantity_in_stock: int
    price: float
    active: bool = True
    category: Optional[str] = None
    min_stock_level: int = 0
    max_stock_level: Optional[int] = None
    last_restock_date: Optional[datetime] = None
    
    def update_stock(self, quantity_change: int) -> bool:
        """Update stock quantity and return True if successful."""
        new_quantity = self.quantity_in_stock + quantity_change
        if new_quantity < 0:
            return False
        if self.max_stock_level and new_quantity > self.max_stock_level:
            return False
        self.quantity_in_stock = new_quantity
        return True

    def needs_restock(self) -> bool:
        """Check if product needs restocking."""
        return self.quantity_in_stock <= self.min_stock_level

    def restock(self, quantity: int) -> bool:
        """Restock the product with the specified quantity."""
        if self.max_stock_level and (self.quantity_in_stock + quantity) > self.max_stock_level:
            return False
        self.quantity_in_stock += quantity
        self.last_restock_date = datetime.now()
        return True

    def deactivate(self) -> None:
        """Deactivate the product."""
        self.active = False

    def activate(self) -> None:
        """Activate the product."""
        self.active = True 
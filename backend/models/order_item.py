from dataclasses import dataclass

@dataclass
class OrderItem:
    """Class representing individual items within an order."""
    orderitem_id: str
    order_id: str
    product_id: str
    quantity: int
    price: float 
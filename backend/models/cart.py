from dataclasses import dataclass
from typing import List, Dict
from .product import Product

@dataclass
class CartItem:
    """Class representing an item in the shopping cart."""
    product: Product
    quantity: int

@dataclass
class Cart:
    """Class representing a shopping cart."""
    cart_id: str
    user_id: str
    items: Dict[str, CartItem] = None

    def __post_init__(self):
        if self.items is None:
            self.items = {}

    def add_item(self, product: Product, quantity: int) -> None:
        """Add a product to the cart."""
        if product.product_id in self.items:
            self.items[product.product_id].quantity += quantity
        else:
            self.items[product.product_id] = CartItem(product, quantity)

    def remove_item(self, product_id: str) -> None:
        """Remove a product from the cart."""
        if product_id in self.items:
            del self.items[product_id]

    def update_quantity(self, product_id: str, quantity: int) -> None:
        """Update the quantity of a product in the cart."""
        if product_id in self.items:
            self.items[product_id].quantity = quantity

    def clear(self) -> None:
        """Clear all items from the cart."""
        self.items = {}

    def get_total(self) -> float:
        """Calculate the total price of items in the cart."""
        return sum(item.product.price * item.quantity for item in self.items.values()) 
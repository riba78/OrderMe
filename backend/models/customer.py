from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .user import User

class PaymentMethod(Base):
    __tablename__ = 'payment_methods'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    type: Mapped[str] = mapped_column(String(50))
    provider: Mapped[str] = mapped_column(String(50))
    last_four: Mapped[str] = mapped_column(String(4))
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PaymentInfo(Base):
    __tablename__ = 'payment_info'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    billing_address: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Customer(User):
    __tablename__ = 'customers'
    __mapper_args__ = {'polymorphic_identity': 'customer'}

    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    shipping_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Relationships
    payment_methods: Mapped[List["PaymentMethod"]] = relationship(lazy="select", backref="customer")
    payment_info: Mapped[Optional["PaymentInfo"]] = relationship(uselist=False, backref="customer")
    
    def add_payment_method(self, payment_method: PaymentMethod) -> None:
        """Add a new payment method."""
        if payment_method.is_default:
            # Set all other payment methods to non-default
            for pm in self.payment_methods:
                pm.is_default = False
        self.payment_methods.append(payment_method)
    
    def get_payment_method(self, payment_id: int) -> Optional[PaymentMethod]:
        """Get a specific payment method by ID."""
        return next((pm for pm in self.payment_methods if pm.id == payment_id), None)
    
    def set_default_payment_method(self, payment_id: int) -> bool:
        """Set a payment method as default."""
        payment_method = self.get_payment_method(payment_id)
        if payment_method:
            for pm in self.payment_methods:
                pm.is_default = (pm.id == payment_id)
            return True
        return False
    
    def update_shipping_address(self, address: str) -> None:
        """Update the shipping address."""
        self.shipping_address = address
        
    def update_phone_number(self, phone: str) -> None:
        """Update the phone number."""
        self.phone_number = phone

    def update_billing_address(self, address: str) -> None:
        """Update the customer's billing address."""
        self.payment_info.billing_address = address

    def add_loyalty_points(self, points: int) -> None:
        """Add loyalty points to the customer's account."""
        # Loyalty points logic would be implemented here
        pass

    def use_loyalty_points(self, points: int) -> bool:
        """Use loyalty points for a purchase."""
        # Loyalty points logic would be implemented here
        return False

    def update_order_stats(self, order_amount: float) -> None:
        """Update customer's order statistics."""
        # Order statistics logic would be implemented here
        pass

    def get_default_payment(self) -> Optional[PaymentInfo]:
        """Get the default payment method."""
        # Default payment logic would be implemented here
        return None

    def remove_payment_method(self, payment_id: int) -> bool:
        """Remove a payment method."""
        payment_method = self.get_payment_method(payment_id)
        if payment_method:
            self.payment_methods.remove(payment_method)
            return True
        return False

    def update_order_stats(self, order_amount: float) -> None:
        """Update customer's order statistics."""
        # Order statistics logic would be implemented here
        pass

    def get_payment_method(self, payment_id: int) -> Optional[PaymentMethod]:
        """Get a specific payment method by ID."""
        return self.get_payment_method(payment_id)

    def update_order_stats(self, order_amount: float) -> None:
        """Update customer's order statistics."""
        # Order statistics logic would be implemented here
        pass

    def get_default_payment(self) -> Optional[PaymentInfo]:
        """Get the default payment method."""
        # Default payment logic would be implemented here
        return None

    def remove_payment_method(self, payment_id: int) -> bool:
        """Remove a payment method."""
        payment_method = self.get_payment_method(payment_id)
        if payment_method:
            self.payment_methods.remove(payment_method)
            return True
        return False

    def update_order_stats(self, order_amount: float) -> None:
        """Update customer's order statistics."""
        # Order statistics logic would be implemented here
        pass

    def get_payment_method(self, payment_id: int) -> Optional[PaymentMethod]:
        """Get a specific payment method by ID."""
        return self.get_payment_method(payment_id)

    def update_order_stats(self, order_amount: float) -> None:
        """Update customer's order statistics."""
        # Order statistics logic would be implemented here
        pass

    def get_default_payment(self) -> Optional[PaymentInfo]:
        """Get the default payment method."""
        # Default payment logic would be implemented here
        return None

    def add_payment_method(self, payment_info: PaymentInfo) -> bool:
        """Add a new payment method."""
        if payment_info.payment_id in self.payment_methods:
            return False
        
        self.payment_methods[payment_info.payment_id] = payment_info
        if payment_info.is_default or not self.default_payment_id:
            self.set_default_payment(payment_info.payment_id)
        return True
    
    def remove_payment_method(self, payment_id: str) -> bool:
        """Remove a payment method."""
        if payment_id not in self.payment_methods:
            return False
        
        if payment_id == self.default_payment_id:
            self.default_payment_id = None
            # Set another payment method as default if available
            if self.payment_methods:
                next_payment = next(iter(self.payment_methods.values()))
                self.set_default_payment(next_payment.payment_id)
                
        del self.payment_methods[payment_id]
        return True
    
    def set_default_payment(self, payment_id: str) -> bool:
        """Set a payment method as default."""
        if payment_id not in self.payment_methods:
            return False
            
        # Remove default flag from current default
        if self.default_payment_id:
            self.payment_methods[self.default_payment_id].is_default = False
            
        self.default_payment_id = payment_id
        self.payment_methods[payment_id].is_default = True
        return True
    
    def get_default_payment(self) -> Optional[PaymentInfo]:
        """Get the default payment method."""
        return self.payment_methods.get(self.default_payment_id) if self.default_payment_id else None
    
    def update_order_stats(self, order_amount: float) -> None:
        """Update customer's order statistics."""
        self.total_orders += 1
        self.total_spent += order_amount
        self.last_order_date = datetime.now()
    
    def get_payment_method(self, payment_id: str) -> Optional[PaymentInfo]:
        """Get a specific payment method."""
        return self.payment_methods.get(payment_id) 
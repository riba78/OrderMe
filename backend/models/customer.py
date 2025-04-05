from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .user import User, UserRole

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
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PaymentInfo(Base):
    __tablename__ = 'payment_info'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    billing_address: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Customer(User):
    """
    Customer model extending the base User model.
    Includes customer-specific fields and assignment relationship.
    """
    __tablename__ = 'customers'
    __mapper_args__ = {'polymorphic_identity': 'customer'}

    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    shipping_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    search_vector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    total_spent: Mapped[float] = mapped_column(Float, default=0.0)
    loyalty_points: Mapped[int] = mapped_column(Integer, default=0)
    last_order_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Assignment relationship
    assigned_to_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey('users.id', name='fk_customer_assigned_to'),
        nullable=True
    )
    last_assigned_by_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('users.id', name='fk_customer_last_assigned_by'),
        nullable=True
    )
    last_assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    assigned_to = relationship(
        'User',
        foreign_keys=[assigned_to_id],
        back_populates='assigned_customers'
    )
    last_assigned_by = relationship(
        'User',
        foreign_keys=[last_assigned_by_id]
    )

    # Relationships
    payment_methods: Mapped[List["PaymentMethod"]] = relationship(lazy="select", backref="customer")
    payment_info: Mapped[Optional["PaymentInfo"]] = relationship(uselist=False, backref="customer")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.role = UserRole.CUSTOMER

    def to_dict(self):
        """Convert customer model to dictionary with all fields."""
        base_dict = super().to_dict()
        base_dict.update({
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'shipping_address': self.shipping_address,
            'total_orders': self.total_orders,
            'total_spent': self.total_spent,
            'loyalty_points': self.loyalty_points,
            'last_order_at': self.last_order_at.isoformat() if self.last_order_at else None,
            'assigned_to': {
                'id': self.assigned_to.id,
                'email': self.assigned_to.email
            } if self.assigned_to else None,
            'last_assigned_by': {
                'id': self.last_assigned_by.id,
                'email': self.last_assigned_by.email
            } if self.last_assigned_by else None,
            'last_assigned_at': self.last_assigned_at.isoformat() if self.last_assigned_at else None
        })
        return base_dict
    
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
        self.phone = phone

    def update_billing_address(self, address: str) -> None:
        """Update the customer's billing address."""
        if not self.payment_info:
            self.payment_info = PaymentInfo(billing_address=address)
        else:
            self.payment_info.billing_address = address

    def add_loyalty_points(self, points: int) -> None:
        """Add loyalty points to the customer's account."""
        self.loyalty_points += points

    def use_loyalty_points(self, points: int) -> bool:
        """Use loyalty points for a purchase."""
        if self.loyalty_points >= points:
            self.loyalty_points -= points
            return True
        return False

    def update_order_stats(self, order_amount: float) -> None:
        """Update customer's order statistics."""
        self.total_orders += 1
        self.total_spent += order_amount
        self.last_order_at = datetime.utcnow()

    def assign_to_user(self, user_id: int, assigned_by_id: int) -> None:
        """Assign the customer to a user."""
        self.assigned_to_id = user_id
        self.last_assigned_by_id = assigned_by_id
        self.last_assigned_at = datetime.utcnow()

    def remove_assignment(self) -> None:
        """Remove the customer's assignment."""
        self.assigned_to_id = None
        self.last_assigned_by_id = None
        self.last_assigned_at = None 
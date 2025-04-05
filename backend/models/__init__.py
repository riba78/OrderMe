"""
Models Package

This package contains all SQLAlchemy models for the application.
"""

from .base import Base
from .user import User, UserRole, VerificationMethod
from .user_profile import UserProfile
from .user_verification_method import UserVerificationMethod
from .customer import Customer, PaymentMethod, PaymentInfo
from .order import Order
from .order_item import OrderItem
from .product import Product
from .cart import Cart
from .chat_session import ChatSession
from .chat_message import ChatMessage
from .ticket import Ticket
from .bill import Bill
from .activity_log import ActivityLog
from .verification_message_log import VerificationMessageLog

from extensions import db

__all__ = [
    'db',
    'Base',
    'User',
    'UserRole',
    'VerificationMethod',
    'UserProfile',
    'UserVerificationMethod',
    'Customer',
    'PaymentMethod',
    'PaymentInfo',
    'Order',
    'OrderItem',
    'Product',
    'Cart',
    'ChatSession',
    'ChatMessage',
    'Ticket',
    'Bill',
    'ActivityLog',
    'VerificationMessageLog'
] 
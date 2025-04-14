"""
Enums Module

This module defines the enumeration types used throughout the application
to ensure type safety and maintain consistent state management.
It includes the following enums:

- UserRole: Defines possible user roles for access control
- OrderStatus: Tracks the lifecycle states of an order
- PaymentStatus: Manages the different states of payment processing
- NotificationType: Categorizes different types of user notifications

These enums are used across multiple modules to:
1. Enforce valid state transitions
2. Maintain data consistency
3. Enable type checking
4. Provide clear documentation of possible values

The enums follow the Single Responsibility Principle by focusing solely
on defining valid states for their respective domains.
"""

import enum

class UserRole(enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    MANAGER = "manager"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class NotificationType(enum.Enum):
    ORDER_STATUS = "order_status"
    PAYMENT = "payment"
    PAYMENT_STATUS = "payment_status"
    SYSTEM = "system" 
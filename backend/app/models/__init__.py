# backend/models/__init__.py

# Import all models from the models directory
from .base import metadata, Base, TimestampMixing
from .user import UserRole, User
from .admin_manager import AdminManager, VerificationMethod
from .customer import Customer

__all__ = [
    "metadata",
    "Base",
    "TimestampMixing",
    "UserRole",
    "User",
    "AdminManager",
    "VerificationMethod",
    "Customer"
]

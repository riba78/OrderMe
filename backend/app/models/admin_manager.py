# extension model for admin_manager, stroing credentials and preferences

import enum
from sqlalchemy import Column, CHAR, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixing

class VerificationMethod(enum.Enum):
    """Enumerated verification methods or password reset for admin managers."""
    whatsapp = "whatsapp"
    email = "email"
    phone = "phone"

class AdminManager(Base, TimestampMixing):
    __tablename__ = "admin_managers"

    id = Column(
        CHAR(36),
        ForeignKey("users.id"),
        primary_key=True
    )

    email = Column(
        CHAR(255),
        nullable=False,
        unique=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    tin_trunk_number = Column(
        String(50),
        nullable=False
    )

    verification_method = Column(
        Enum(VerificationMethod),
        nullable=False,
        default=VerificationMethod.email
    )

    user = relationship(
        "User", back_populates="admin_manager"
    )

    def __repr__(self):
        return(
            f"<Adminmanager(id={self.id}, email=self{self.email}, "
            f"method={self.verification_method.name})>"
        )





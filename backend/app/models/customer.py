# extension model for customer, including contact phone and assigment fields

from sqlalchemy import Column, CHAR, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixing

class Customer(Base, TimestampMixing):
    __tablename__ = "customers"

    id = Column(
        CHAR(36),
        primary_key=True
    )

    phone = Column(
        String(20),
        nullable=False
    )

    created_by = Column(
        CHAR(36),
        ForeignKey("users.id"),
        nullable=False
    )

    assigned_manager_id = Column(
        CHAR(36),
        ForeignKey("users.id"),
        nullable=True
    )

    create_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_customers"
    )

    assigned_manager = relationship(
        "User",
        foreign_keys=[assigned_manager_id],
        back_populates="assigned_customers"
    )

    def __repr__(self):
        return(
            f"<Customer(id={self.id}, phone={self.phone}, "
            f"<created_by={self.created_by}, assigned_manager={self.assigned_manager_id})>"
        )


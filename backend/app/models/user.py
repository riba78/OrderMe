# SQLAlchemy model for 'users', including enums, glags, and relationships to extension 
# tables.
import enum
import uuid
from sqlalchemy import Column, Enum, Boolean, CHAR
from sqlalchemy.orm import relationship, foreign
from .base import Base, TimestampMixing
from .customer import Customer 

class UserRole(enum.Enum):
    """Enumerated User roles with associated permissions."""
    admin = "admin"
    manager = "manager"
    customer = "customer"

class User(Base, TimestampMixing):
    __tablename__ = "users"

    id = Column(
        CHAR(36),
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
        )
    
    role = Column(
        Enum(UserRole),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )
    
    admin_manager = relationship(
        "AdminManager", uselist=False, back_populates="user"
    )
    
    created_customers = relationship(
        "Customer",
        foreign_keys="Customer.created_by",
        back_populates="create_by_user"
    )
    assigned_customers = relationship(
        "Customer",
        foreign_keys="Customer.assigned_manager_id",
        back_populates="assigned_manager"
    )
    customer = relationship(
        "Customer",
        uselist=False,
        backref="user",
        primaryjoin="User.id==foreign(Customer.id)"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, role={self.role}, is_active={self.is_active})>"
    
    

    



    


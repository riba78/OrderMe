# Defines the SQLAlchemy declarative base with async support, naming conventions, and a timestamp mixin
# for 'create_at'/'updated_at' fields

from sqlalchemy import MetaData, Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs

# Enforce consistent naming for constrains and indexes
default_naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_label)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_label)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=default_naming_convention)

# AsyncAttrs enables async ORM methods on models
Base = declarative_base(metadata=metadata, cls=AsyncAttrs)

class TimestampMixing:
    """Add created_at and updated_at columns with automatic timestamps."""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

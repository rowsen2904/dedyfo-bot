"""Database base model and utilities."""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower() + 's'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """String representation of the model."""
        class_name = self.__class__.__name__
        attrs = []
        for column in self.__table__.columns:
            if hasattr(self, column.name):
                attrs.append(f"{column.name}={getattr(self, column.name)!r}")
        return f"{class_name}({', '.join(attrs)})"


class TimestampMixin:
    """Mixin for adding timestamp fields."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

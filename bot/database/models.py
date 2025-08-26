"""Database models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    BLOCKED = "blocked"
    BANNED = "banned"


class User(Base, TimestampMixin):
    """User model."""
    
    # Telegram user ID as primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    # User information
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Bot-specific fields
    status: Mapped[UserStatus] = mapped_column(
        String(20), 
        default=UserStatus.ACTIVE,
        nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    
    # Interaction tracking
    first_interaction: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    last_interaction: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Statistics
    total_messages: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    
    # Relationships
    analytics: Mapped[list["Analytics"]] = relationship(
        "Analytics", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        parts = [self.first_name, self.last_name]
        return " ".join(part for part in parts if part) or self.username or f"User_{self.id}"
    
    @property
    def mention(self) -> str:
        """Get user mention for Telegram."""
        if self.username:
            return f"@{self.username}"
        return f'<a href="tg://user?id={self.id}">{self.full_name}</a>'


class ActionType(str, Enum):
    """Analytics action types."""
    START = "start"
    HELP = "help"
    ABOUT = "about"
    PORTFOLIO = "portfolio"
    QUOTES = "quotes"
    WEATHER = "weather"
    NEWS = "news"
    ADMIN_PANEL = "admin_panel"
    SETTINGS = "settings"
    FEEDBACK = "feedback"
    ERROR = "error"


class Analytics(Base, TimestampMixin):
    """Analytics model for tracking user actions."""
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # User reference
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Action details
    action: Mapped[ActionType] = mapped_column(String(50), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Context
    chat_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    message_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Timing
    response_time_ms: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="analytics")


class NotificationType(str, Enum):
    """Notification types."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    ADMIN = "admin"


class NotificationStatus(str, Enum):
    """Notification status."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Notification(Base, TimestampMixin):
    """Notification model."""
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # User reference (nullable for broadcast messages)
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True
    )
    
    # Notification content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[NotificationType] = mapped_column(String(20), nullable=False)
    
    # Scheduling
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Status tracking
    status: Mapped[NotificationStatus] = mapped_column(
        String(20),
        default=NotificationStatus.PENDING,
        nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    is_broadcast: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="notifications")

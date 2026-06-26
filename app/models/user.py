import uuid
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class UserRole(str, PyEnum):
    user = "user"
    agent = "agent"
    admin = "admin"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    whatsapp: Mapped[Optional[str]] = mapped_column(String(20))
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    district: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    properties: Mapped[List["Property"]] = relationship("Property", back_populates="owner", lazy="select")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="guest", lazy="select")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="reviewer", lazy="select")
    sent_messages: Mapped[List["Message"]] = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", lazy="select")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", lazy="select")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="user", lazy="select")
    saved_properties: Mapped[List["SavedProperty"]] = relationship("SavedProperty", back_populates="user", lazy="select")
    unlock_credits: Mapped[List["UnlockCredit"]] = relationship("UnlockCredit", back_populates="user", lazy="select")


class SavedProperty(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "saved_properties"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="saved_properties")
    property: Mapped["Property"] = relationship("Property", back_populates="saved_by")


class UnlockCredit(Base, UUIDMixin, TimestampMixin):
    """Tracks which properties a user has unlocked (to see owner contacts)."""
    __tablename__ = "unlock_credits"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="unlock_credits")
    property: Mapped["Property"] = relationship("Property")

import uuid
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class NotificationType(str, PyEnum):
    booking_request = "booking_request"
    booking_confirmed = "booking_confirmed"
    booking_cancelled = "booking_cancelled"
    new_message = "new_message"
    new_review = "new_review"
    property_unlocked = "property_unlocked"
    payment_success = "payment_success"
    system = "system"


class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    action_url: Mapped[Optional[str]] = mapped_column(String(512))
    related_id: Mapped[Optional[str]] = mapped_column(String(100))  # booking_id, property_id, etc.

    user: Mapped["User"] = relationship("User", back_populates="notifications")

import uuid
from datetime import date
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class BookingStatus(str, PyEnum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    no_show = "no_show"


class Booking(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "bookings"

    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    guest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    guests: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Pricing snapshot (frozen at booking time)
    price_per_night: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    nights: Mapped[int] = mapped_column(Integer, nullable=False)
    cleaning_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.pending, nullable=False, index=True)
    special_requests: Mapped[Optional[str]] = mapped_column(Text)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(500))

    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="bookings")
    guest: Mapped["User"] = relationship("User", back_populates="bookings")
    payment: Mapped[Optional["Payment"]] = relationship("Payment", back_populates="booking", uselist=False)
    review: Mapped[Optional["Review"]] = relationship("Review", back_populates="booking", uselist=False)

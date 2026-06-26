import uuid
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class PaymentStatus(str, PyEnum):
    pending = "pending"
    processing = "processing"
    success = "success"
    failed = "failed"
    refunded = "refunded"


class PaymentType(str, PyEnum):
    booking = "booking"
    listing_package = "listing_package"
    unlock_property = "unlock_property"
    unlock_pack = "unlock_pack"


class PaymentMethod(str, PyEnum):
    mtn_momo = "mtn_momo"
    airtel_money = "airtel_money"
    card = "card"


class Payment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payments"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="SET NULL"))

    type: Mapped[PaymentType] = mapped_column(Enum(PaymentType), nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(5), default="UGX")
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.pending, nullable=False, index=True)

    # MTN MoMo / provider reference
    provider_ref: Mapped[Optional[str]] = mapped_column(String(255))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    description: Mapped[Optional[str]] = mapped_column(String(500))

    user: Mapped["User"] = relationship("User", back_populates="payments")
    booking: Mapped[Optional["Booking"]] = relationship("Booking", back_populates="payment")

import uuid
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Review(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating"),
    )

    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    booking_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="SET NULL"))

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Granular scores (1–5)
    cleanliness: Mapped[Optional[int]] = mapped_column(Integer)
    location: Mapped[Optional[int]] = mapped_column(Integer)
    value: Mapped[Optional[int]] = mapped_column(Integer)
    communication: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="reviews")
    reviewer: Mapped["User"] = relationship("User", back_populates="reviews")
    booking: Mapped[Optional["Booking"]] = relationship("Booking", back_populates="review")

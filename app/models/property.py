import uuid
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class PropertyStatus(str, PyEnum):
    for_rent = "for_rent"
    for_sale = "for_sale"
    for_lease = "for_lease"


class PropertyType(str, PyEnum):
    house = "house"
    apartment = "apartment"
    office = "office"
    land = "land"
    warehouse = "warehouse"
    commercial = "commercial"
    short_stay = "short_stay"
    holiday_apt = "holiday_apt"


class ListingPackage(str, PyEnum):
    basic = "basic"
    premium = "premium"
    featured = "featured"


class Property(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "properties"

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[PropertyType] = mapped_column(Enum(PropertyType), nullable=False)
    status: Mapped[PropertyStatus] = mapped_column(Enum(PropertyStatus), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    exact_location: Mapped[Optional[str]] = mapped_column(String(500))

    # Contact (revealed only after unlock)
    owner_phone: Mapped[Optional[str]] = mapped_column(String(20))
    owner_whatsapp: Mapped[Optional[str]] = mapped_column(String(20))

    # Specs
    bedrooms: Mapped[Optional[int]] = mapped_column(Integer)
    bathrooms: Mapped[Optional[int]] = mapped_column(Integer)
    parking_spaces: Mapped[Optional[int]] = mapped_column(Integer)
    plot_size: Mapped[Optional[float]] = mapped_column(Float)
    floor_size: Mapped[Optional[float]] = mapped_column(Float)

    # Amenities
    has_security: Mapped[bool] = mapped_column(Boolean, default=False)
    has_furnishing: Mapped[bool] = mapped_column(Boolean, default=False)
    has_internet: Mapped[bool] = mapped_column(Boolean, default=False)
    has_swimming_pool: Mapped[bool] = mapped_column(Boolean, default=False)
    has_gym: Mapped[bool] = mapped_column(Boolean, default=False)
    has_generator: Mapped[bool] = mapped_column(Boolean, default=False)
    has_water_tank: Mapped[bool] = mapped_column(Boolean, default=False)
    has_solar: Mapped[bool] = mapped_column(Boolean, default=False)

    # Location
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)

    # Short-stay specific
    is_short_stay: Mapped[bool] = mapped_column(Boolean, default=False)
    price_per_night: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    max_guests: Mapped[Optional[int]] = mapped_column(Integer)
    min_nights: Mapped[Optional[int]] = mapped_column(Integer)
    cleaning_fee: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    # Aggregate stats (cached, updated via trigger or service)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    # Admin / moderation
    listing_package: Mapped[ListingPackage] = mapped_column(Enum(ListingPackage), default=ListingPackage.basic)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="properties")
    photos: Mapped[List["PropertyPhoto"]] = relationship("PropertyPhoto", back_populates="property", cascade="all, delete-orphan", order_by="PropertyPhoto.order")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="property", lazy="select")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="property", lazy="select")
    saved_by: Mapped[List["SavedProperty"]] = relationship("SavedProperty", back_populates="property", lazy="select")


class PropertyPhoto(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "property_photos"

    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(512))
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False)

    property: Mapped["Property"] = relationship("Property", back_populates="photos")

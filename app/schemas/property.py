import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator
from app.models.property import PropertyStatus, PropertyType, ListingPackage


class PropertyPhotoOut(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    url: str
    thumbnail_url: Optional[str]
    order: int
    is_cover: bool


class PropertyCreate(BaseModel):
    title: str
    type: PropertyType
    status: PropertyStatus
    price: float
    district: str
    area: str
    description: str
    exact_location: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_whatsapp: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    plot_size: Optional[float] = None
    floor_size: Optional[float] = None
    has_security: bool = False
    has_furnishing: bool = False
    has_internet: bool = False
    has_swimming_pool: bool = False
    has_gym: bool = False
    has_generator: bool = False
    has_water_tank: bool = False
    has_solar: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_short_stay: bool = False
    price_per_night: Optional[float] = None
    max_guests: Optional[int] = None
    min_nights: Optional[int] = None
    cleaning_fee: Optional[float] = None
    listing_package: ListingPackage = ListingPackage.basic

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    exact_location: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_whatsapp: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    plot_size: Optional[float] = None
    floor_size: Optional[float] = None
    has_security: Optional[bool] = None
    has_furnishing: Optional[bool] = None
    has_internet: Optional[bool] = None
    has_swimming_pool: Optional[bool] = None
    has_gym: Optional[bool] = None
    has_generator: Optional[bool] = None
    has_water_tank: Optional[bool] = None
    has_solar: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_short_stay: Optional[bool] = None
    price_per_night: Optional[float] = None
    max_guests: Optional[int] = None
    min_nights: Optional[int] = None
    cleaning_fee: Optional[float] = None


class PropertyOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    type: PropertyType
    status: PropertyStatus
    price: float
    district: str
    area: str
    description: str
    exact_location: Optional[str]
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    parking_spaces: Optional[int]
    plot_size: Optional[float]
    floor_size: Optional[float]
    has_security: bool
    has_furnishing: bool
    has_internet: bool
    has_swimming_pool: bool
    has_gym: bool
    has_generator: bool
    has_water_tank: bool
    has_solar: bool
    latitude: Optional[float]
    longitude: Optional[float]
    is_short_stay: bool
    price_per_night: Optional[float]
    max_guests: Optional[int]
    min_nights: Optional[int]
    cleaning_fee: Optional[float]
    rating: float
    review_count: int
    view_count: int
    listing_package: ListingPackage
    is_verified: bool
    is_active: bool
    is_featured: bool
    photos: List[PropertyPhotoOut] = []
    created_at: datetime
    updated_at: datetime

    # Contact — set to None if not unlocked; service layer handles this
    owner_phone: Optional[str] = None
    owner_whatsapp: Optional[str] = None


class PropertyCard(BaseModel):
    """Lightweight card for listing views."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    type: PropertyType
    status: PropertyStatus
    price: float
    district: str
    area: str
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    floor_size: Optional[float]
    is_short_stay: bool
    price_per_night: Optional[float]
    rating: float
    review_count: int
    is_verified: bool
    is_featured: bool
    listing_package: ListingPackage
    cover_photo: Optional[str] = None
    created_at: datetime


class PropertyMapPin(BaseModel):
    model_config = {"from_attributes": True}
    id: uuid.UUID
    title: str
    price: float
    latitude: float
    longitude: float
    type: PropertyType
    status: PropertyStatus


class PropertyFilter(BaseModel):
    status: Optional[PropertyStatus] = None
    type: Optional[PropertyType] = None
    district: Optional[str] = None
    area: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    is_short_stay: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_featured: Optional[bool] = None
    has_swimming_pool: Optional[bool] = None
    has_furnishing: Optional[bool] = None
    has_internet: Optional[bool] = None
    has_security: Optional[bool] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = 1
    size: int = 20

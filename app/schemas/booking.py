import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    property_id: uuid.UUID
    check_in: date
    check_out: date
    guests: int = 1
    special_requests: Optional[str] = None

    @field_validator("check_out")
    @classmethod
    def checkout_after_checkin(cls, v: date, info) -> date:
        if "check_in" in info.data and v <= info.data["check_in"]:
            raise ValueError("check_out must be after check_in")
        return v

    @field_validator("guests")
    @classmethod
    def guests_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("At least 1 guest required")
        return v


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    cancellation_reason: Optional[str] = None


class BookingOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    property_id: uuid.UUID
    guest_id: uuid.UUID
    check_in: date
    check_out: date
    guests: int
    price_per_night: float
    nights: int
    cleaning_fee: float
    total_amount: float
    status: BookingStatus
    special_requests: Optional[str]
    cancellation_reason: Optional[str]
    created_at: datetime

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class ReviewCreate(BaseModel):
    property_id: uuid.UUID
    booking_id: Optional[uuid.UUID] = None
    rating: int
    comment: Optional[str] = None
    cleanliness: Optional[int] = None
    location: Optional[int] = None
    value: Optional[int] = None
    communication: Optional[int] = None

    @field_validator("rating", "cleanliness", "location", "value", "communication", mode="before")
    @classmethod
    def rating_range(cls, v):
        if v is not None and not (1 <= v <= 5):
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    property_id: uuid.UUID
    reviewer_id: uuid.UUID
    booking_id: Optional[uuid.UUID]
    rating: int
    comment: Optional[str]
    cleanliness: Optional[int]
    location: Optional[int]
    value: Optional[int]
    communication: Optional[int]
    created_at: datetime

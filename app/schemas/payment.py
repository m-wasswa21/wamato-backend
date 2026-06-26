import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.payment import PaymentStatus, PaymentType, PaymentMethod


class InitiatePaymentRequest(BaseModel):
    type: PaymentType
    method: PaymentMethod
    phone_number: str
    amount: float
    currency: str = "UGX"
    booking_id: Optional[uuid.UUID] = None
    property_id: Optional[uuid.UUID] = None
    description: Optional[str] = None


class PaymentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    booking_id: Optional[uuid.UUID]
    type: PaymentType
    method: PaymentMethod
    amount: float
    currency: str
    status: PaymentStatus
    provider_ref: Optional[str]
    description: Optional[str]
    created_at: datetime


class PaymentCallback(BaseModel):
    """MTN MoMo / Airtel Money callback payload."""
    provider_ref: str
    status: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    phone_number: Optional[str] = None

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    full_name: str
    email: EmailStr
    phone: Optional[str]
    whatsapp: Optional[str]
    role: UserRole
    avatar_url: Optional[str]
    bio: Optional[str]
    district: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime


class UserPublic(BaseModel):
    """Minimal user info exposed to other users."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    full_name: str
    avatar_url: Optional[str]
    is_verified: bool
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    bio: Optional[str] = None
    district: Optional[str] = None


class UserAdminUpdate(UserUpdate):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.property import (
    PropertyCreate, PropertyUpdate, PropertyOut,
    PropertyCard, PropertyFilter, PropertyMapPin,
)
from app.schemas.common import Paginated, MessageResponse
from app.services.property import PropertyService
from app.services.upload import UploadService
from app.api.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.get("", response_model=Paginated[PropertyCard])
async def list_properties(
    status: Optional[str] = None,
    type: Optional[str] = None,
    district: Optional[str] = None,
    area: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    bedrooms: Optional[int] = None,
    is_short_stay: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    filters = PropertyFilter(
        status=status, type=type, district=district, area=area,
        min_price=min_price, max_price=max_price, bedrooms=bedrooms,
        is_short_stay=is_short_stay, is_featured=is_featured,
        sort_by=sort_by, sort_order=sort_order, page=page, size=size,
    )
    return await PropertyService.list_properties(db, filters)


@router.get("/map", response_model=List[PropertyMapPin])
async def map_pins(
    district: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    return await PropertyService.get_map_pins(db, district=district, status=status)


@router.get("/featured", response_model=List[PropertyCard])
async def featured(limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await PropertyService.get_featured(db, limit)


@router.get("/my", response_model=Paginated[PropertyCard])
async def my_listings(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await PropertyService.get_owner_listings(db, current_user.id, page, size)


@router.post("", response_model=PropertyOut, status_code=201)
async def create_property(
    body: PropertyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await PropertyService.create(db, body, current_user.id)


@router.get("/{property_id}", response_model=PropertyOut)
async def get_property(
    property_id: uuid.UUID,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id if current_user else None
    return await PropertyService.get_detail(db, property_id, user_id)


@router.patch("/{property_id}", response_model=PropertyOut)
async def update_property(
    property_id: uuid.UUID,
    body: PropertyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await PropertyService.update(db, property_id, body, current_user)


@router.delete("/{property_id}", response_model=MessageResponse)
async def delete_property(
    property_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await PropertyService.delete(db, property_id, current_user)
    return {"message": "Property deleted"}


@router.post("/{property_id}/photos", response_model=PropertyOut)
async def upload_photos(
    property_id: uuid.UUID,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await PropertyService.add_photos(db, property_id, files, current_user)


@router.delete("/{property_id}/photos/{photo_id}", response_model=MessageResponse)
async def delete_photo(
    property_id: uuid.UUID,
    photo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await PropertyService.delete_photo(db, property_id, photo_id, current_user)
    return {"message": "Photo deleted"}


@router.post("/{property_id}/unlock", response_model=MessageResponse)
async def unlock_property(
    property_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await PropertyService.unlock(db, property_id, current_user.id)
    return {"message": "Property unlocked"}


@router.post("/{property_id}/view", response_model=MessageResponse)
async def record_view(property_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await PropertyService.increment_view(db, property_id)
    return {"message": "View recorded"}


# Admin
@router.patch("/{property_id}/verify", response_model=PropertyOut, dependencies=[Depends(require_admin)])
async def verify_property(property_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await PropertyService.set_verified(db, property_id, True)


@router.patch("/{property_id}/feature", response_model=PropertyOut, dependencies=[Depends(require_admin)])
async def feature_property(property_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await PropertyService.set_featured(db, property_id, True)

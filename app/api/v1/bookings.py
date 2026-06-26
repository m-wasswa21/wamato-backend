import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.booking import BookingCreate, BookingUpdate, BookingOut
from app.schemas.common import Paginated, MessageResponse
from app.services.booking import BookingService
from app.api.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingOut, status_code=201)
async def create_booking(
    body: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await BookingService.create(db, body, current_user.id)


@router.get("/my", response_model=Paginated[BookingOut])
async def my_bookings(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await BookingService.get_guest_bookings(db, current_user.id, page, size)


@router.get("/incoming", response_model=Paginated[BookingOut])
async def incoming_bookings(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await BookingService.get_host_bookings(db, current_user.id, page, size)


@router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await BookingService.get(db, booking_id, current_user.id)


@router.patch("/{booking_id}", response_model=BookingOut)
async def update_booking(
    booking_id: uuid.UUID,
    body: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await BookingService.update(db, booking_id, body, current_user)


@router.post("/{booking_id}/cancel", response_model=BookingOut)
async def cancel_booking(
    booking_id: uuid.UUID,
    reason: str = "",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await BookingService.cancel(db, booking_id, current_user.id, reason)


# Admin
@router.get("", response_model=Paginated[BookingOut], dependencies=[Depends(require_admin)])
async def list_all_bookings(
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await BookingService.list_all(db, page, size)

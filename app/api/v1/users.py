import uuid
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserOut, UserUpdate, UserAdminUpdate
from app.schemas.property import PropertyCard
from app.schemas.common import Paginated, MessageResponse
from app.services.user import UserService
from app.services.upload import UploadService
from app.api.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService.update(db, current_user, body)


@router.post("/me/avatar", response_model=UserOut)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    url = await UploadService.upload_avatar(file, str(current_user.id))
    return await UserService.set_avatar(db, current_user, url)


@router.get("/me/saved-properties", response_model=Paginated[PropertyCard])
async def saved_properties(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService.get_saved_properties(db, current_user.id, page, size)


@router.post("/me/saved-properties/{property_id}", response_model=MessageResponse)
async def save_property(
    property_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await UserService.save_property(db, current_user.id, property_id)
    return {"message": "Property saved"}


@router.delete("/me/saved-properties/{property_id}", response_model=MessageResponse)
async def unsave_property(
    property_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await UserService.unsave_property(db, current_user.id, property_id)
    return {"message": "Property removed from saved"}


# ── Admin endpoints ────────────────────────────────────────────────────────────
@router.get("", response_model=Paginated[UserOut], dependencies=[Depends(require_admin)])
async def list_users(page: int = 1, size: int = 20, db: AsyncSession = Depends(get_db)):
    return await UserService.list_users(db, page, size)


@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(require_admin)])
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await UserService.get_by_id(db, user_id)


@router.patch("/{user_id}", response_model=UserOut, dependencies=[Depends(require_admin)])
async def admin_update_user(
    user_id: uuid.UUID,
    body: UserAdminUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await UserService.admin_update(db, user_id, body)

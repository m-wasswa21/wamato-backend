from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.notification import NotificationOut
from app.schemas.common import Paginated, MessageResponse
from app.services.notification import NotificationService
from app.api.deps import get_current_user
from app.models.user import User
import uuid

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=Paginated[NotificationOut])
async def get_notifications(
    page: int = 1,
    size: int = 30,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await NotificationService.get_user_notifications(db, current_user.id, page, size, unread_only)


@router.post("/{notif_id}/read", response_model=MessageResponse)
async def mark_read(
    notif_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await NotificationService.mark_read(db, notif_id, current_user.id)
    return {"message": "Marked as read"}


@router.post("/read-all", response_model=MessageResponse)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await NotificationService.mark_all_read(db, current_user.id)
    return {"message": "All notifications marked as read"}

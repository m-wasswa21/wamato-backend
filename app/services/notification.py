import uuid
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.models.notification import Notification, NotificationType
from app.schemas.common import Paginated
from app.core.exceptions import NotFound, Forbidden


class NotificationService:

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: uuid.UUID,
        type: NotificationType,
        title: str,
        body: str,
        action_url: str = None,
        related_id: str = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id, type=type, title=title, body=body,
            action_url=action_url, related_id=related_id,
        )
        db.add(notif)
        await db.flush()
        return notif

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession, user_id: uuid.UUID, page: int, size: int, unread_only: bool
    ) -> Paginated:
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read == False)
        total_res = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_res.scalar_one()
        offset = (page - 1) * size
        res = await db.execute(query.order_by(Notification.created_at.desc()).offset(offset).limit(size))
        items = res.scalars().all()
        return Paginated(items=items, total=total, page=page, size=size, pages=math.ceil(total / size) if total else 0)

    @staticmethod
    async def mark_read(db: AsyncSession, notif_id: uuid.UUID, user_id: uuid.UUID) -> None:
        res = await db.execute(select(Notification).where(Notification.id == notif_id))
        notif = res.scalar_one_or_none()
        if not notif:
            raise NotFound("Notification")
        if notif.user_id != user_id:
            raise Forbidden()
        notif.is_read = True
        db.add(notif)

    @staticmethod
    async def mark_all_read(db: AsyncSession, user_id: uuid.UUID) -> None:
        await db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True)
        )

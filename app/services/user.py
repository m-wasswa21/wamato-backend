import uuid
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.models.user import User, SavedProperty
from app.models.property import Property, PropertyPhoto
from app.schemas.user import UserUpdate, UserAdminUpdate
from app.schemas.property import PropertyCard
from app.schemas.common import Paginated
from app.core.exceptions import NotFound


class UserService:

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFound("User")
        return user

    @staticmethod
    async def update(db: AsyncSession, user: User, body: UserUpdate) -> User:
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        db.add(user)
        return user

    @staticmethod
    async def set_avatar(db: AsyncSession, user: User, url: str) -> User:
        user.avatar_url = url
        db.add(user)
        return user

    @staticmethod
    async def admin_update(db: AsyncSession, user_id: uuid.UUID, body: UserAdminUpdate) -> User:
        user = await UserService.get_by_id(db, user_id)
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        db.add(user)
        return user

    @staticmethod
    async def list_users(db: AsyncSession, page: int, size: int) -> Paginated:
        offset = (page - 1) * size
        total_res = await db.execute(select(func.count()).select_from(User))
        total = total_res.scalar_one()
        res = await db.execute(select(User).offset(offset).limit(size).order_by(User.created_at.desc()))
        users = res.scalars().all()
        return Paginated(items=users, total=total, page=page, size=size, pages=math.ceil(total / size))

    @staticmethod
    async def save_property(db: AsyncSession, user_id: uuid.UUID, property_id: uuid.UUID) -> None:
        exists = await db.execute(
            select(SavedProperty).where(
                SavedProperty.user_id == user_id,
                SavedProperty.property_id == property_id,
            )
        )
        if exists.scalar_one_or_none():
            return
        db.add(SavedProperty(user_id=user_id, property_id=property_id))

    @staticmethod
    async def unsave_property(db: AsyncSession, user_id: uuid.UUID, property_id: uuid.UUID) -> None:
        await db.execute(
            delete(SavedProperty).where(
                SavedProperty.user_id == user_id,
                SavedProperty.property_id == property_id,
            )
        )

    @staticmethod
    async def get_saved_properties(db: AsyncSession, user_id: uuid.UUID, page: int, size: int) -> Paginated:
        offset = (page - 1) * size
        total_res = await db.execute(
            select(func.count()).select_from(SavedProperty).where(SavedProperty.user_id == user_id)
        )
        total = total_res.scalar_one()
        res = await db.execute(
            select(Property)
            .join(SavedProperty, SavedProperty.property_id == Property.id)
            .where(SavedProperty.user_id == user_id)
            .options(selectinload(Property.photos))
            .offset(offset).limit(size)
        )
        properties = res.scalars().all()
        cards = [_to_card(p) for p in properties]
        return Paginated(items=cards, total=total, page=page, size=size, pages=math.ceil(total / size))


def _to_card(p: Property) -> PropertyCard:
    cover = next((ph.url for ph in p.photos if ph.is_cover), None)
    if cover is None and p.photos:
        cover = p.photos[0].url
    return PropertyCard(
        id=p.id, title=p.title, type=p.type, status=p.status, price=p.price,
        district=p.district, area=p.area, bedrooms=p.bedrooms, bathrooms=p.bathrooms,
        floor_size=p.floor_size, is_short_stay=p.is_short_stay,
        price_per_night=p.price_per_night, rating=p.rating, review_count=p.review_count,
        is_verified=p.is_verified, is_featured=p.is_featured,
        listing_package=p.listing_package, cover_photo=cover, created_at=p.created_at,
    )

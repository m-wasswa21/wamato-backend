import uuid
import math
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, or_
from sqlalchemy.orm import selectinload

from app.models.property import Property, PropertyPhoto, PropertyStatus, PropertyType
from app.models.user import User, UserRole, UnlockCredit
from app.schemas.property import (
    PropertyCreate, PropertyUpdate, PropertyOut, PropertyCard,
    PropertyFilter, PropertyMapPin,
)
from app.schemas.common import Paginated
from app.services.upload import UploadService
from app.core.exceptions import NotFound, Forbidden
import math


class PropertyService:

    @staticmethod
    async def create(db: AsyncSession, body: PropertyCreate, owner_id: uuid.UUID) -> Property:
        prop = Property(owner_id=owner_id, **body.model_dump())
        db.add(prop)
        await db.flush()
        await db.refresh(prop, ["photos"])
        return prop

    @staticmethod
    async def get_detail(db: AsyncSession, property_id: uuid.UUID, user_id: Optional[uuid.UUID]) -> PropertyOut:
        result = await db.execute(
            select(Property)
            .options(selectinload(Property.photos))
            .where(Property.id == property_id, Property.is_active == True)
        )
        prop = result.scalar_one_or_none()
        if not prop:
            raise NotFound("Property")

        out = PropertyOut.model_validate(prop)

        # Only reveal contacts if user has unlocked or is the owner
        is_owner = user_id and prop.owner_id == user_id
        unlocked = False
        if user_id and not is_owner:
            res = await db.execute(
                select(UnlockCredit).where(
                    UnlockCredit.user_id == user_id,
                    UnlockCredit.property_id == property_id,
                )
            )
            unlocked = res.scalar_one_or_none() is not None

        if not is_owner and not unlocked:
            out.owner_phone = None
            out.owner_whatsapp = None

        return out

    @staticmethod
    async def list_properties(db: AsyncSession, filters: PropertyFilter) -> Paginated[PropertyCard]:
        query = (
            select(Property)
            .options(selectinload(Property.photos))
            .where(Property.is_active == True)
        )
        if filters.status:
            query = query.where(Property.status == filters.status)
        if filters.type:
            query = query.where(Property.type == filters.type)
        if filters.district:
            query = query.where(Property.district.ilike(f"%{filters.district}%"))
        if filters.area:
            query = query.where(Property.area.ilike(f"%{filters.area}%"))
        if filters.min_price is not None:
            query = query.where(Property.price >= filters.min_price)
        if filters.max_price is not None:
            query = query.where(Property.price <= filters.max_price)
        if filters.bedrooms is not None:
            query = query.where(Property.bedrooms >= filters.bedrooms)
        if filters.is_short_stay is not None:
            query = query.where(Property.is_short_stay == filters.is_short_stay)
        if filters.is_featured is not None:
            query = query.where(Property.is_featured == filters.is_featured)
        if filters.is_verified is not None:
            query = query.where(Property.is_verified == filters.is_verified)
        if filters.has_swimming_pool:
            query = query.where(Property.has_swimming_pool == True)
        if filters.has_furnishing:
            query = query.where(Property.has_furnishing == True)
        if filters.has_internet:
            query = query.where(Property.has_internet == True)
        if filters.has_security:
            query = query.where(Property.has_security == True)

        sort_col = getattr(Property, filters.sort_by, Property.created_at)
        query = query.order_by(sort_col.desc() if filters.sort_order == "desc" else sort_col.asc())

        total_res = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_res.scalar_one()

        offset = (filters.page - 1) * filters.size
        res = await db.execute(query.offset(offset).limit(filters.size))
        props = res.scalars().all()

        cards = [_to_card(p) for p in props]
        return Paginated(items=cards, total=total, page=filters.page, size=filters.size, pages=math.ceil(total / filters.size) if total else 0)

    @staticmethod
    async def get_featured(db: AsyncSession, limit: int) -> List[PropertyCard]:
        res = await db.execute(
            select(Property)
            .options(selectinload(Property.photos))
            .where(Property.is_featured == True, Property.is_active == True)
            .order_by(Property.created_at.desc())
            .limit(limit)
        )
        return [_to_card(p) for p in res.scalars().all()]

    @staticmethod
    async def get_map_pins(db: AsyncSession, district: Optional[str], status: Optional[str]) -> List[PropertyMapPin]:
        query = select(Property).where(
            Property.is_active == True,
            Property.latitude.is_not(None),
            Property.longitude.is_not(None),
        )
        if district:
            query = query.where(Property.district.ilike(f"%{district}%"))
        if status:
            query = query.where(Property.status == status)
        res = await db.execute(query)
        return [PropertyMapPin.model_validate(p) for p in res.scalars().all()]

    @staticmethod
    async def get_owner_listings(db: AsyncSession, owner_id: uuid.UUID, page: int, size: int) -> Paginated[PropertyCard]:
        total_res = await db.execute(
            select(func.count()).select_from(Property).where(
                Property.owner_id == owner_id, Property.is_active == True
            )
        )
        total = total_res.scalar_one()
        offset = (page - 1) * size
        res = await db.execute(
            select(Property)
            .options(selectinload(Property.photos))
            .where(Property.owner_id == owner_id, Property.is_active == True)
            .order_by(Property.created_at.desc())
            .offset(offset).limit(size)
        )
        cards = [_to_card(p) for p in res.scalars().all()]
        return Paginated(items=cards, total=total, page=page, size=size, pages=math.ceil(total / size) if total else 0)

    @staticmethod
    async def update(db: AsyncSession, property_id: uuid.UUID, body: PropertyUpdate, current_user: User) -> Property:
        prop = await _get_or_404(db, property_id)
        _assert_owner_or_admin(prop, current_user)
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(prop, field, value)
        db.add(prop)
        await db.refresh(prop, ["photos"])
        return prop

    @staticmethod
    async def delete(db: AsyncSession, property_id: uuid.UUID, current_user: User) -> None:
        prop = await _get_or_404(db, property_id)
        _assert_owner_or_admin(prop, current_user)
        prop.is_active = False
        db.add(prop)
        await db.flush()

    @staticmethod
    async def add_photos(db: AsyncSession, property_id: uuid.UUID, files: List[UploadFile], current_user: User) -> Property:
        prop = await _get_or_404(db, property_id)
        _assert_owner_or_admin(prop, current_user)
        existing_count = len(prop.photos) if prop.photos else 0
        for i, file in enumerate(files):
            url, thumb = await UploadService.upload_property_image(file, str(property_id))
            photo = PropertyPhoto(
                property_id=property_id,
                url=url,
                thumbnail_url=thumb,
                order=existing_count + i,
                is_cover=(existing_count == 0 and i == 0),
            )
            db.add(photo)
        await db.flush()
        await db.refresh(prop, ["photos"])
        return prop

    @staticmethod
    async def delete_photo(db: AsyncSession, property_id: uuid.UUID, photo_id: uuid.UUID, current_user: User) -> None:
        prop = await _get_or_404(db, property_id)
        _assert_owner_or_admin(prop, current_user)
        res = await db.execute(select(PropertyPhoto).where(PropertyPhoto.id == photo_id, PropertyPhoto.property_id == property_id))
        photo = res.scalar_one_or_none()
        if photo:
            await db.delete(photo)

    @staticmethod
    async def unlock(db: AsyncSession, property_id: uuid.UUID, user_id: uuid.UUID) -> None:
        res = await db.execute(
            select(UnlockCredit).where(UnlockCredit.user_id == user_id, UnlockCredit.property_id == property_id)
        )
        if not res.scalar_one_or_none():
            db.add(UnlockCredit(user_id=user_id, property_id=property_id))

    @staticmethod
    async def increment_view(db: AsyncSession, property_id: uuid.UUID) -> None:
        await db.execute(
            update(Property).where(Property.id == property_id).values(view_count=Property.view_count + 1)
        )

    @staticmethod
    async def set_verified(db: AsyncSession, property_id: uuid.UUID, val: bool) -> Property:
        prop = await _get_or_404(db, property_id)
        prop.is_verified = val
        db.add(prop)
        await db.refresh(prop, ["photos"])
        return prop

    @staticmethod
    async def set_featured(db: AsyncSession, property_id: uuid.UUID, val: bool) -> Property:
        prop = await _get_or_404(db, property_id)
        prop.is_featured = val
        db.add(prop)
        await db.refresh(prop, ["photos"])
        return prop


async def _get_or_404(db: AsyncSession, property_id: uuid.UUID) -> Property:
    res = await db.execute(
        select(Property).options(selectinload(Property.photos)).where(Property.id == property_id)
    )
    prop = res.scalar_one_or_none()
    if not prop:
        raise NotFound("Property")
    return prop


def _assert_owner_or_admin(prop: Property, user: User) -> None:
    if prop.owner_id != user.id and user.role != UserRole.admin:
        raise Forbidden("You do not own this property")


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

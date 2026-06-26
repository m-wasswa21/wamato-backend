import math
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models.property import Property
from app.schemas.property import PropertyCard
from app.schemas.common import Paginated


class SearchService:

    @staticmethod
    async def full_text_search(
        db: AsyncSession, q: str, district: Optional[str], page: int, size: int
    ) -> Paginated[PropertyCard]:
        term = f"%{q}%"
        query = (
            select(Property)
            .options(selectinload(Property.photos))
            .where(
                Property.is_active == True,
                or_(
                    Property.title.ilike(term),
                    Property.area.ilike(term),
                    Property.district.ilike(term),
                    Property.description.ilike(term),
                ),
            )
        )
        if district:
            query = query.where(Property.district.ilike(f"%{district}%"))

        total_res = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_res.scalar_one()
        offset = (page - 1) * size
        res = await db.execute(query.order_by(Property.is_featured.desc(), Property.created_at.desc()).offset(offset).limit(size))
        props = res.scalars().all()
        cards = [_to_card(p) for p in props]
        return Paginated(items=cards, total=total, page=page, size=size, pages=math.ceil(total / size) if total else 0)

    @staticmethod
    async def autocomplete(db: AsyncSession, q: str) -> List[str]:
        term = f"{q}%"
        areas_res = await db.execute(
            select(Property.area).where(Property.area.ilike(term), Property.is_active == True).distinct().limit(5)
        )
        districts_res = await db.execute(
            select(Property.district).where(Property.district.ilike(term), Property.is_active == True).distinct().limit(5)
        )
        suggestions = [r[0] for r in areas_res.all()] + [r[0] for r in districts_res.all()]
        return list(dict.fromkeys(suggestions))[:8]  # deduplicate, cap at 8


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

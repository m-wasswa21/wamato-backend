import uuid
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.models.review import Review
from app.models.property import Property
from app.models.user import User, UserRole
from app.schemas.review import ReviewCreate
from app.schemas.common import Paginated
from app.core.exceptions import NotFound, Forbidden, Conflict


class ReviewService:

    @staticmethod
    async def create(db: AsyncSession, body: ReviewCreate, reviewer_id: uuid.UUID) -> Review:
        # Prevent duplicate reviews for same property by same user
        existing = await db.execute(
            select(Review).where(Review.property_id == body.property_id, Review.reviewer_id == reviewer_id)
        )
        if existing.scalar_one_or_none():
            raise Conflict("You have already reviewed this property")

        review = Review(reviewer_id=reviewer_id, **body.model_dump())
        db.add(review)
        await db.flush()

        # Update property aggregate rating
        agg = await db.execute(
            select(func.avg(Review.rating), func.count(Review.id))
            .where(Review.property_id == body.property_id)
        )
        avg_rating, count = agg.one()
        await db.execute(
            update(Property)
            .where(Property.id == body.property_id)
            .values(rating=round(float(avg_rating or 0), 2), review_count=count)
        )
        await db.refresh(review)
        return review

    @staticmethod
    async def get_for_property(db: AsyncSession, property_id: uuid.UUID, page: int, size: int) -> Paginated:
        total_res = await db.execute(
            select(func.count()).select_from(Review).where(Review.property_id == property_id)
        )
        total = total_res.scalar_one()
        offset = (page - 1) * size
        res = await db.execute(
            select(Review)
            .where(Review.property_id == property_id)
            .order_by(Review.created_at.desc())
            .offset(offset).limit(size)
        )
        items = res.scalars().all()
        return Paginated(items=items, total=total, page=page, size=size, pages=math.ceil(total / size) if total else 0)

    @staticmethod
    async def delete(db: AsyncSession, review_id: uuid.UUID, user: User) -> None:
        res = await db.execute(select(Review).where(Review.id == review_id))
        review = res.scalar_one_or_none()
        if not review:
            raise NotFound("Review")
        if review.reviewer_id != user.id and user.role != UserRole.admin:
            raise Forbidden()
        await db.delete(review)

        # Recalculate rating
        agg = await db.execute(
            select(func.avg(Review.rating), func.count(Review.id))
            .where(Review.property_id == review.property_id)
        )
        avg_rating, count = agg.one()
        await db.execute(
            update(Property)
            .where(Property.id == review.property_id)
            .values(rating=round(float(avg_rating or 0), 2), review_count=count)
        )

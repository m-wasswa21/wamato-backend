import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.review import ReviewCreate, ReviewOut
from app.schemas.common import Paginated
from app.services.review import ReviewService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewOut, status_code=201)
async def create_review(
    body: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ReviewService.create(db, body, current_user.id)


@router.get("/property/{property_id}", response_model=Paginated[ReviewOut])
async def property_reviews(
    property_id: uuid.UUID,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await ReviewService.get_for_property(db, property_id, page, size)


@router.delete("/{review_id}")
async def delete_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ReviewService.delete(db, review_id, current_user)
    return {"message": "Review deleted"}

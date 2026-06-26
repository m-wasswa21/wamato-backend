from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.property import PropertyCard
from app.schemas.common import Paginated
from app.services.search import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=Paginated[PropertyCard])
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    district: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await SearchService.full_text_search(db, q, district, page, size)


@router.get("/suggestions", response_model=List[str])
async def suggestions(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    return await SearchService.autocomplete(db, q)

import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.payment import InitiatePaymentRequest, PaymentOut, PaymentCallback
from app.schemas.common import Paginated, MessageResponse
from app.services.payment import PaymentService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/initiate", response_model=PaymentOut, status_code=201)
async def initiate_payment(
    body: InitiatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await PaymentService.initiate(db, body, current_user.id)


@router.get("/my", response_model=Paginated[PaymentOut])
async def my_payments(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await PaymentService.get_user_payments(db, current_user.id, page, size)


@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await PaymentService.get(db, payment_id, current_user.id)


@router.post("/callback/mtn", response_model=MessageResponse)
async def mtn_callback(body: PaymentCallback, db: AsyncSession = Depends(get_db)):
    """MTN MoMo webhook — called by MTN after payment confirmation."""
    await PaymentService.handle_callback(db, body)
    return {"message": "OK"}


@router.post("/callback/airtel", response_model=MessageResponse)
async def airtel_callback(body: PaymentCallback, db: AsyncSession = Depends(get_db)):
    await PaymentService.handle_callback(db, body)
    return {"message": "OK"}

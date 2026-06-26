import uuid
import math
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.models.payment import Payment, PaymentStatus, PaymentType, PaymentMethod
from app.models.booking import Booking, BookingStatus
from app.schemas.payment import InitiatePaymentRequest, PaymentOut, PaymentCallback
from app.schemas.common import Paginated
from app.core.config import settings
from app.core.exceptions import NotFound, Forbidden, BadRequest
from app.core.logging import logger


class PaymentService:

    @staticmethod
    async def initiate(db: AsyncSession, body: InitiatePaymentRequest, user_id: uuid.UUID) -> Payment:
        payment = Payment(
            user_id=user_id,
            booking_id=body.booking_id,
            type=body.type,
            method=body.method,
            amount=body.amount,
            currency=body.currency,
            phone_number=body.phone_number,
            description=body.description,
            status=PaymentStatus.pending,
        )
        db.add(payment)
        await db.flush()

        # Dispatch to provider
        if body.method == PaymentMethod.mtn_momo:
            ref = await _request_mtn_payment(body.phone_number, body.amount, str(payment.id))
        else:
            ref = f"AIRTEL-{payment.id}"  # stub for Airtel Money

        payment.provider_ref = ref
        payment.status = PaymentStatus.processing
        db.add(payment)
        await db.flush()
        await db.refresh(payment)
        return payment

    @staticmethod
    async def get(db: AsyncSession, payment_id: uuid.UUID, user_id: uuid.UUID) -> Payment:
        res = await db.execute(select(Payment).where(Payment.id == payment_id))
        payment = res.scalar_one_or_none()
        if not payment:
            raise NotFound("Payment")
        if payment.user_id != user_id:
            raise Forbidden()
        return payment

    @staticmethod
    async def get_user_payments(db: AsyncSession, user_id: uuid.UUID, page: int, size: int) -> Paginated:
        total_res = await db.execute(
            select(func.count()).select_from(Payment).where(Payment.user_id == user_id)
        )
        total = total_res.scalar_one()
        offset = (page - 1) * size
        res = await db.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .offset(offset).limit(size)
        )
        return Paginated(items=res.scalars().all(), total=total, page=page, size=size, pages=math.ceil(total / size) if total else 0)

    @staticmethod
    async def handle_callback(db: AsyncSession, body: PaymentCallback) -> None:
        res = await db.execute(select(Payment).where(Payment.provider_ref == body.provider_ref))
        payment = res.scalar_one_or_none()
        if not payment:
            logger.warning("Payment callback for unknown ref", ref=body.provider_ref)
            return

        new_status = PaymentStatus.success if body.status in ("SUCCESSFUL", "SUCCESS") else PaymentStatus.failed
        payment.status = new_status
        db.add(payment)

        # Auto-confirm booking on successful payment
        if new_status == PaymentStatus.success and payment.booking_id:
            await db.execute(
                update(Booking)
                .where(Booking.id == payment.booking_id)
                .values(status=BookingStatus.confirmed)
            )


async def _request_mtn_payment(phone: str, amount: float, external_id: str) -> str:
    """Initiate MTN MoMo Collection request. Returns provider reference."""
    if not settings.MTN_MOMO_PRIMARY_KEY:
        # Sandbox stub
        return f"MTN-STUB-{external_id}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.MTN_MOMO_URL}/collection/v1_0/requesttopay",
                json={
                    "amount": str(int(amount)),
                    "currency": "UGX",
                    "externalId": external_id,
                    "payer": {"partyIdType": "MSISDN", "partyId": phone},
                    "payerMessage": "Wamato payment",
                    "payeeNote": "Wamato",
                },
                headers={
                    "Authorization": f"Bearer {settings.MTN_MOMO_API_KEY}",
                    "X-Reference-Id": external_id,
                    "X-Target-Environment": settings.MTN_MOMO_ENV,
                    "Ocp-Apim-Subscription-Key": settings.MTN_MOMO_PRIMARY_KEY,
                    "Content-Type": "application/json",
                },
                timeout=15,
            )
            resp.raise_for_status()
            return external_id
    except Exception as e:
        logger.error("MTN MoMo request failed", error=str(e))
        raise BadRequest("Payment initiation failed. Please try again.")

"""
Background tasks for Wamato.
Run worker: celery -A app.workers.celery_app worker --loglevel=info
"""
import asyncio
from app.workers.celery_app import celery_app
from app.core.logging import logger


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_booking_confirmation_email(self, booking_id: str, guest_email: str, guest_name: str):
    """Send booking confirmation email to guest."""
    try:
        logger.info("Sending booking confirmation", booking_id=booking_id, email=guest_email)
        # TODO: integrate SendGrid / SMTP
        # send_email(to=guest_email, subject="Booking Confirmed", template="booking_confirm", ...)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_booking_request_to_host(self, booking_id: str, host_email: str, property_title: str):
    """Notify host of a new booking request."""
    try:
        logger.info("Notifying host of booking request", booking_id=booking_id, host=host_email)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def check_payment_status(self, payment_id: str):
    """Poll MTN MoMo for payment status if callback hasn't arrived."""
    from app.core.database import AsyncSessionLocal
    from app.models.payment import Payment, PaymentStatus
    from sqlalchemy import select

    async def _check():
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(Payment).where(Payment.id == payment_id))
            payment = res.scalar_one_or_none()
            if not payment or payment.status != PaymentStatus.processing:
                return
            logger.info("Checking payment status", payment_id=payment_id)
            # TODO: call MTN MoMo status endpoint
    try:
        _run(_check())
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task
def cleanup_expired_pending_bookings():
    """Daily task: cancel bookings still in 'pending' after 24 hours without payment."""
    from app.core.database import AsyncSessionLocal
    from app.models.booking import Booking, BookingStatus
    from sqlalchemy import select, update
    from datetime import datetime, timedelta, timezone

    async def _cleanup():
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Booking)
                .where(Booking.status == BookingStatus.pending, Booking.created_at < cutoff)
                .values(status=BookingStatus.cancelled, cancellation_reason="Payment timeout")
            )
            await db.commit()
            logger.info("Expired pending bookings cleaned up")
    _run(_cleanup())


# Celery Beat schedule (add to settings if needed)
celery_app.conf.beat_schedule = {
    "cleanup-expired-bookings-daily": {
        "task": "app.workers.tasks.cleanup_expired_pending_bookings",
        "schedule": 86400,  # every 24h
    },
}

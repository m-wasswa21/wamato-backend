import uuid
import math
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.booking import Booking, BookingStatus
from app.models.property import Property
from app.models.user import User, UserRole
from app.schemas.booking import BookingCreate, BookingUpdate, BookingOut
from app.schemas.common import Paginated
from app.core.exceptions import NotFound, Forbidden, BadRequest


class BookingService:

    @staticmethod
    async def create(db: AsyncSession, body: BookingCreate, guest_id: uuid.UUID) -> Booking:
        res = await db.execute(select(Property).where(Property.id == body.property_id, Property.is_active == True))
        prop = res.scalar_one_or_none()
        if not prop:
            raise NotFound("Property")
        if not prop.is_short_stay:
            raise BadRequest("This property does not accept short-stay bookings")
        if prop.max_guests and body.guests > prop.max_guests:
            raise BadRequest(f"Max guests allowed: {prop.max_guests}")

        # Check for overlapping confirmed bookings
        overlap = await db.execute(
            select(Booking).where(
                Booking.property_id == body.property_id,
                Booking.status == BookingStatus.confirmed,
                and_(Booking.check_in < body.check_out, Booking.check_out > body.check_in),
            )
        )
        if overlap.scalar_one_or_none():
            raise BadRequest("Property is not available for the selected dates")

        nights = (body.check_out - body.check_in).days
        if prop.min_nights and nights < prop.min_nights:
            raise BadRequest(f"Minimum stay is {prop.min_nights} night(s)")

        ppn = float(prop.price_per_night or prop.price)
        cleaning_fee = float(prop.cleaning_fee or 0)
        total = ppn * nights + cleaning_fee

        booking = Booking(
            property_id=body.property_id,
            guest_id=guest_id,
            check_in=body.check_in,
            check_out=body.check_out,
            guests=body.guests,
            price_per_night=ppn,
            nights=nights,
            cleaning_fee=cleaning_fee,
            total_amount=total,
            special_requests=body.special_requests,
        )
        db.add(booking)
        await db.flush()
        await db.refresh(booking)
        return booking

    @staticmethod
    async def get(db: AsyncSession, booking_id: uuid.UUID, user_id: uuid.UUID) -> Booking:
        res = await db.execute(select(Booking).where(Booking.id == booking_id))
        booking = res.scalar_one_or_none()
        if not booking:
            raise NotFound("Booking")
        return booking

    @staticmethod
    async def update(db: AsyncSession, booking_id: uuid.UUID, body: BookingUpdate, user: User) -> Booking:
        res = await db.execute(select(Booking).where(Booking.id == booking_id))
        booking = res.scalar_one_or_none()
        if not booking:
            raise NotFound("Booking")
        # Only host or admin can confirm/cancel
        prop_res = await db.execute(select(Property).where(Property.id == booking.property_id))
        prop = prop_res.scalar_one()
        is_host = prop.owner_id == user.id
        if not is_host and user.role != UserRole.admin:
            raise Forbidden()
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(booking, field, value)
        db.add(booking)
        return booking

    @staticmethod
    async def cancel(db: AsyncSession, booking_id: uuid.UUID, user_id: uuid.UUID, reason: str) -> Booking:
        res = await db.execute(select(Booking).where(Booking.id == booking_id))
        booking = res.scalar_one_or_none()
        if not booking:
            raise NotFound("Booking")
        if booking.guest_id != user_id:
            raise Forbidden()
        booking.status = BookingStatus.cancelled
        booking.cancellation_reason = reason
        db.add(booking)
        return booking

    @staticmethod
    async def get_guest_bookings(db: AsyncSession, guest_id: uuid.UUID, page: int, size: int) -> Paginated:
        return await _paginate(db, select(Booking).where(Booking.guest_id == guest_id), page, size)

    @staticmethod
    async def get_host_bookings(db: AsyncSession, host_id: uuid.UUID, page: int, size: int) -> Paginated:
        query = (
            select(Booking)
            .join(Property, Property.id == Booking.property_id)
            .where(Property.owner_id == host_id)
        )
        return await _paginate(db, query, page, size)

    @staticmethod
    async def list_all(db: AsyncSession, page: int, size: int) -> Paginated:
        return await _paginate(db, select(Booking), page, size)


async def _paginate(db: AsyncSession, query, page: int, size: int) -> Paginated:
    total_res = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_res.scalar_one()
    offset = (page - 1) * size
    res = await db.execute(query.offset(offset).limit(size).order_by(Booking.created_at.desc()))
    items = res.scalars().all()
    return Paginated(items=items, total=total, page=page, size=size, pages=math.ceil(total / size) if total else 0)

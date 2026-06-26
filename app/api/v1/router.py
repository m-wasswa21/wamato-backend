from fastapi import APIRouter
from app.api.v1 import auth, users, properties, bookings, reviews, messages, payments, notifications, search

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(properties.router)
router.include_router(bookings.router)
router.include_router(reviews.router)
router.include_router(messages.router)
router.include_router(payments.router)
router.include_router(notifications.router)
router.include_router(search.router)

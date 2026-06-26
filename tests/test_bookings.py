import pytest
from datetime import date, timedelta
from httpx import AsyncClient

SHORT_STAY_PROPERTY = {
    "title": "Airbnb Kololo",
    "type": "short_stay",
    "status": "for_rent",
    "price": 120000,
    "district": "Kampala",
    "area": "Kololo",
    "description": "Short stay apartment",
    "is_short_stay": True,
    "price_per_night": 120000,
    "max_guests": 4,
    "min_nights": 1,
    "cleaning_fee": 30000,
    "listing_package": "basic",
}


async def _register_and_login(client: AsyncClient, email: str, password: str = "Test@1234") -> dict:
    await client.post("/api/v1/auth/register", json={"full_name": "User", "email": email, "password": password})
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.mark.asyncio
async def test_create_booking(client: AsyncClient):
    host = await _register_and_login(client, "host_b@wamato.ug")
    guest = await _register_and_login(client, "guest_b@wamato.ug")

    create = await client.post("/api/v1/properties", json=SHORT_STAY_PROPERTY, headers=host)
    prop_id = create.json()["id"]

    check_in = (date.today() + timedelta(days=5)).isoformat()
    check_out = (date.today() + timedelta(days=8)).isoformat()

    resp = await client.post("/api/v1/bookings", json={
        "property_id": prop_id,
        "check_in": check_in,
        "check_out": check_out,
        "guests": 2,
    }, headers=guest)
    assert resp.status_code == 201
    data = resp.json()
    assert data["nights"] == 3
    assert data["total_amount"] == 3 * 120000 + 30000


@pytest.mark.asyncio
async def test_cannot_book_non_short_stay(client: AsyncClient):
    host = await _register_and_login(client, "host_c@wamato.ug")
    guest = await _register_and_login(client, "guest_c@wamato.ug")

    long_term = {**SHORT_STAY_PROPERTY, "type": "house", "is_short_stay": False}
    create = await client.post("/api/v1/properties", json=long_term, headers=host)
    prop_id = create.json()["id"]

    resp = await client.post("/api/v1/bookings", json={
        "property_id": prop_id,
        "check_in": (date.today() + timedelta(days=1)).isoformat(),
        "check_out": (date.today() + timedelta(days=3)).isoformat(),
        "guests": 1,
    }, headers=guest)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_cancel_booking(client: AsyncClient):
    host = await _register_and_login(client, "host_d@wamato.ug")
    guest = await _register_and_login(client, "guest_d@wamato.ug")

    create = await client.post("/api/v1/properties", json=SHORT_STAY_PROPERTY, headers=host)
    prop_id = create.json()["id"]

    booking = await client.post("/api/v1/bookings", json={
        "property_id": prop_id,
        "check_in": (date.today() + timedelta(days=10)).isoformat(),
        "check_out": (date.today() + timedelta(days=12)).isoformat(),
        "guests": 1,
    }, headers=guest)
    booking_id = booking.json()["id"]

    resp = await client.post(f"/api/v1/bookings/{booking_id}/cancel?reason=Plans+changed", headers=guest)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"

import pytest
from httpx import AsyncClient

PROPERTY_PAYLOAD = {
    "title": "Test House Kololo",
    "type": "house",
    "status": "for_rent",
    "price": 2000000,
    "district": "Kampala",
    "area": "Kololo",
    "description": "A lovely test house",
    "bedrooms": 3,
    "bathrooms": 2,
    "listing_package": "basic",
}


@pytest.mark.asyncio
async def test_create_property(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test House Kololo"
    assert data["district"] == "Kampala"


@pytest.mark.asyncio
async def test_list_properties(client: AsyncClient):
    resp = await client.get("/api/v1/properties")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_property_detail(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=auth_headers)
    prop_id = create.json()["id"]
    resp = await client.get(f"/api/v1/properties/{prop_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == prop_id


@pytest.mark.asyncio
async def test_update_property(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=auth_headers)
    prop_id = create.json()["id"]
    resp = await client.patch(f"/api/v1/properties/{prop_id}", json={"price": 3000000}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["price"] == 3000000


@pytest.mark.asyncio
async def test_search_properties(client: AsyncClient, auth_headers: dict):
    await client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=auth_headers)
    resp = await client.get("/api/v1/search?q=Kololo")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_filter_by_status(client: AsyncClient):
    resp = await client.get("/api/v1/properties?status=for_rent")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_property(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/v1/properties", json=PROPERTY_PAYLOAD, headers=auth_headers)
    prop_id = create.json()["id"]
    resp = await client.delete(f"/api/v1/properties/{prop_id}", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_contact_hidden_without_unlock(client: AsyncClient, auth_headers: dict):
    payload = {**PROPERTY_PAYLOAD, "owner_phone": "+256700000099", "owner_whatsapp": "+256700000099"}
    create = await client.post("/api/v1/properties", json=payload, headers=auth_headers)
    prop_id = create.json()["id"]

    # Register a second user and get their token
    await client.post("/api/v1/auth/register", json={
        "full_name": "Other User", "email": "other@wamato.ug", "password": "Other@1234"
    })
    login = await client.post("/api/v1/auth/login", json={"email": "other@wamato.ug", "password": "Other@1234"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = await client.get(f"/api/v1/properties/{prop_id}", headers=other_headers)
    assert resp.json()["owner_phone"] is None

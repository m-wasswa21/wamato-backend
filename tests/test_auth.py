import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "full_name": "Jane Doe",
        "email": "jane@wamato.ug",
        "password": "Secure@123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "jane@wamato.ug"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {"full_name": "Dup User", "email": "dup@wamato.ug", "password": "Secure@123"}
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "full_name": "Login User", "email": "login@wamato.ug", "password": "Secure@123"
    })
    resp = await client.post("/api/v1/auth/login", json={"email": "login@wamato.ug", "password": "Secure@123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert "refresh_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={"email": "testuser@wamato.ug", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "testuser@wamato.ug"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "full_name": "Refresh User", "email": "refresh@wamato.ug", "password": "Secure@123"
    })
    login = await client.post("/api/v1/auth/login", json={"email": "refresh@wamato.ug", "password": "Secure@123"})
    refresh_token = login.json()["refresh_token"]
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

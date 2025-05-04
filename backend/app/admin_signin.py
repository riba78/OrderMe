# run from backend: pytest app/admin_signin.py
# run backend server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_admin_signin_success():
    async with AsyncClient(app=app, base_url="http://test", lifespan="on") as ac:
        response = await ac.post(
            "/auth/signin",
            json={"email": "admin@orderme.com", "password": "admin123"}
        )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_admin_signin_wrong_password():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/signin",
            json={"email": "admin@orderme.com", "password": "wrongpassword"}
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_admin_signin_nonexistent_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/signin",
            json={"email": "notfound@orderme.com", "password": "irrelevant"}
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"
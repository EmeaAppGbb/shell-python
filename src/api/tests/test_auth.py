"""Tests for authentication endpoints."""

from httpx import AsyncClient

from tests.conftest import register_user

# ── Register ────────────────────────────────────────────────────────────────


class TestRegister:
    async def test_register_first_user_gets_admin(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register", json={"username": "admin01", "password": "securepass1"}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["message"] == "Registration successful"
        assert data["role"] == "admin"
        assert "token" in resp.cookies

    async def test_register_second_user_gets_user_role(self, client: AsyncClient):
        await register_user(client, "first", "password123")
        resp = await client.post(
            "/api/auth/register", json={"username": "second", "password": "password123"}
        )
        assert resp.status_code == 201
        assert resp.json()["role"] == "user"

    async def test_register_duplicate_username(self, client: AsyncClient):
        await register_user(client, "dupuser", "password123")
        resp = await client.post(
            "/api/auth/register", json={"username": "dupuser", "password": "password123"}
        )
        assert resp.status_code == 409
        assert "already exists" in resp.json()["error"].lower()

    async def test_register_short_password(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register", json={"username": "validuser", "password": "short"}
        )
        assert resp.status_code == 400

    async def test_register_invalid_username(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register", json={"username": "a", "password": "password123"}
        )
        assert resp.status_code == 400

    async def test_register_missing_fields(self, client: AsyncClient):
        resp = await client.post("/api/auth/register", json={})
        assert resp.status_code == 400


# ── Login ───────────────────────────────────────────────────────────────────


class TestLogin:
    async def test_login_success(self, client: AsyncClient):
        await register_user(client, "loginuser", "password123")
        resp = await client.post(
            "/api/auth/login", json={"username": "loginuser", "password": "password123"}
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Login successful"
        assert "token" in resp.cookies

    async def test_login_wrong_password(self, client: AsyncClient):
        await register_user(client, "loginuser", "password123")
        resp = await client.post(
            "/api/auth/login", json={"username": "loginuser", "password": "wrongpass"}
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/login", json={"username": "ghost", "password": "password123"}
        )
        assert resp.status_code == 401


# ── Logout ──────────────────────────────────────────────────────────────────


class TestLogout:
    async def test_logout_clears_cookie(self, client: AsyncClient):
        await register_user(client, "logoutuser", "password123")
        resp = await client.post("/api/auth/logout")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Logged out successfully"


# ── Me ──────────────────────────────────────────────────────────────────────


class TestMe:
    async def test_me_authenticated(self, client: AsyncClient):
        reg = await register_user(client, "meuser", "password123")
        token = reg["cookies"].get("token")
        resp = await client.get("/api/auth/me", cookies={"token": token})
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "meuser"
        assert data["role"] == "admin"
        assert "createdAt" in data

    async def test_me_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401

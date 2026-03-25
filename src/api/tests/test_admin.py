"""Tests for admin endpoints."""

from httpx import AsyncClient

from tests.conftest import register_user


class TestAdminUsers:
    async def test_list_users_as_admin(self, client: AsyncClient):
        reg = await register_user(client, "adminuser", "password123")
        token = reg["cookies"].get("token")

        # Register a second user
        await client.post(
            "/api/auth/register", json={"username": "regular", "password": "password123"}
        )

        resp = await client.get("/api/admin/users", cookies={"token": token})
        assert resp.status_code == 200
        users = resp.json()
        assert len(users) == 2
        usernames = [u["username"] for u in users]
        assert "adminuser" in usernames
        assert "regular" in usernames

    async def test_list_users_as_non_admin(self, client: AsyncClient):
        # First user = admin
        await register_user(client, "adminuser", "password123")
        # Second user = regular
        reg2 = await client.post(
            "/api/auth/register", json={"username": "regular", "password": "password123"}
        )
        token = reg2.cookies.get("token")

        resp = await client.get("/api/admin/users", cookies={"token": token})
        assert resp.status_code == 403

    async def test_list_users_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/admin/users")
        assert resp.status_code == 401


class TestHealth:
    async def test_health_endpoint(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

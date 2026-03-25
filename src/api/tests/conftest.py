"""Shared test fixtures."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.db import clear_users
from app.main import app


@pytest.fixture(autouse=True)
def _reset_store():
    """Clear the in-memory store before every test for isolation."""
    clear_users()
    yield
    clear_users()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client wired to the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def register_user(
    client: AsyncClient,
    username: str = "testuser",
    password: str = "password123",
) -> dict:
    """Helper: register a user and return the response."""
    resp = await client.post("/api/auth/register", json={"username": username, "password": password})
    return {"response": resp, "cookies": resp.cookies}


async def login_user(
    client: AsyncClient,
    username: str = "testuser",
    password: str = "password123",
) -> dict:
    """Helper: log in a user and return the response."""
    resp = await client.post("/api/auth/login", json={"username": username, "password": password})
    return {"response": resp, "cookies": resp.cookies}

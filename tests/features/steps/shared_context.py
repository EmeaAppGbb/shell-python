"""
Shared context helpers for Behave step definitions.

Provides utility functions for auth operations used across step files.
"""

import httpx
from typing import Any


def register_user(context, username: str, password: str) -> httpx.Response:
    """Register a user via the API and store the response."""
    resp = context.client.post(
        "/api/auth/register",
        json={"username": username, "password": password},
    )
    context.response = resp
    try:
        context.last_json = resp.json()
    except Exception:
        context.last_json = None
    return resp


def login_user(context, username: str, password: str) -> httpx.Response:
    """Log in a user via the API and store cookies for subsequent requests."""
    resp = context.client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    context.response = resp
    try:
        context.last_json = resp.json()
    except Exception:
        context.last_json = None
    # Capture cookies (especially the JWT token)
    context.cookies = dict(resp.cookies)
    return resp


def get_auth_cookies(context) -> dict[str, str]:
    """Return the current auth cookies for authenticated requests."""
    return context.cookies


def make_authenticated_request(
    context, method: str, path: str, **kwargs: Any
) -> httpx.Response:
    """Make an authenticated HTTP request using stored cookies."""
    resp = context.client.request(
        method, path, cookies=context.cookies, **kwargs
    )
    context.response = resp
    try:
        context.last_json = resp.json()
    except Exception:
        context.last_json = None
    return resp

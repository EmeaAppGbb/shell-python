"""JWT authentication middleware for FastAPI."""

import logging
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class JwtPayload:
    sub: str
    username: str
    role: str


def get_current_user(token: Annotated[str | None, Cookie()] = None) -> JwtPayload:
    """Extract and verify JWT from the 'token' cookie."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return JwtPayload(sub=payload["sub"], username=payload["username"], role=payload["role"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Not authenticated") from None
    except (jwt.InvalidTokenError, KeyError):
        raise HTTPException(status_code=401, detail="Not authenticated") from None


def require_admin(user: Annotated[JwtPayload, Depends(get_current_user)]) -> JwtPayload:
    """Verify the authenticated user has the admin role."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user

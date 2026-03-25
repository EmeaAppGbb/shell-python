"""Admin endpoints: user management."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from app.db import get_all_users
from app.middleware.auth import JwtPayload, require_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
async def list_users(_user: Annotated[JwtPayload, Depends(require_admin)]) -> list[dict]:
    users = get_all_users()
    return [
        {
            "username": u.username,
            "role": u.role,
            "createdAt": u.created_at.isoformat(),
        }
        for u in users
    ]

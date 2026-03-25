"""Authentication endpoints: register, login, logout, me."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Response

from app.config import settings
from app.db import add_user, get_all_users, get_user_by_id, get_user_by_username
from app.middleware.auth import JwtPayload, get_current_user
from app.models import LoginRequest, MessageResponse, RegisterRequest, RegisterResponse, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_token_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/",
        max_age=86400,
    )


def _create_token(user_id: str, username: str, role: str) -> str:
    return jwt.encode(
        {
            "sub": user_id,
            "username": username,
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours),
        },
        settings.jwt_secret,
        algorithm="HS256",
    )


@router.post("/register", status_code=201, response_model=RegisterResponse)
async def register(body: RegisterRequest, response: Response) -> RegisterResponse:
    if get_user_by_username(body.username):
        raise HTTPException(status_code=409, detail="Username already exists")

    password_hash = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    role = "admin" if len(get_all_users()) == 0 else "user"

    user_id = str(uuid.uuid4())
    add_user(
        User(
            id=user_id,
            username=body.username,
            password_hash=password_hash,
            role=role,
            created_at=datetime.now(timezone.utc),
        )
    )

    token = _create_token(user_id, body.username, role)
    _set_token_cookie(response, token)

    logger.info("User registered: %s (role=%s)", body.username, role)
    return RegisterResponse(message="Registration successful", role=role)


@router.post("/login", response_model=MessageResponse)
async def login(body: LoginRequest, response: Response) -> MessageResponse:
    if not body.username or not body.password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    user = get_user_by_username(body.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not bcrypt.checkpw(body.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = _create_token(user.id, user.username, user.role)
    _set_token_cookie(response, token)

    logger.info("User logged in: %s", body.username)
    return MessageResponse(message="Login successful")


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response) -> MessageResponse:
    response.delete_cookie(key="token", httponly=True, secure=True, samesite="strict", path="/")
    return MessageResponse(message="Logged out successfully")


@router.get("/me")
async def me(user: Annotated[JwtPayload, Depends(get_current_user)]) -> dict:
    db_user = get_user_by_id(user.sub)
    if not db_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "username": db_user.username,
        "role": db_user.role,
        "createdAt": db_user.created_at.isoformat(),
    }

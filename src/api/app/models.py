"""Pydantic v2 models for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,30}$"


# ── Request models ──────────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=USERNAME_REGEX)
    password: str = Field(..., min_length=8)

    @field_validator("username")
    @classmethod
    def username_format(cls, v: str) -> str:
        import re

        if not re.match(USERNAME_REGEX, v):
            raise ValueError(
                "Username must be between 3 and 30 characters and contain only "
                "letters, numbers, and underscores"
            )
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


# ── Response models ─────────────────────────────────────────────────────────


class MessageResponse(BaseModel):
    message: str


class RegisterResponse(BaseModel):
    message: str
    role: str


class ErrorResponse(BaseModel):
    error: str
    details: str | None = None


class UserProfile(BaseModel):
    username: str
    role: str
    created_at: str = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class HealthResponse(BaseModel):
    status: str
    timestamp: str


# ── Internal domain model ──────────────────────────────────────────────────


class User(BaseModel):
    id: str
    username: str
    password_hash: str
    role: str  # "admin" | "user"
    created_at: datetime

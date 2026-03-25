"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import admin, auth

# ── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("spec2cloud API starting up")
    yield
    logger.info("spec2cloud API shutting down")


# ── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(title="spec2cloud API", version="1.0.0", lifespan=lifespan)

# CORS — allow all origins for dev (tighten for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(admin.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/info")
async def info() -> dict:
    return {"version": "1.0.0", "framework": "spec2cloud"}


# ── Exception handlers — match TypeScript shell error format ────────────────


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return {"error": "..."} to match the TypeScript shell format."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert FastAPI 422 → 400 with user-friendly messages matching the TS shell."""
    errors = exc.errors()
    if errors:
        first = errors[0]
        field = str(first.get("loc", ["", "body", "unknown"])[-1]).lower()
        if "username" in field:
            detail = (
                "Username must be between 3 and 30 characters and contain only "
                "letters, numbers, and underscores"
            )
        elif "password" in field:
            detail = "Password must be at least 8 characters"
        else:
            detail = first.get("msg", "Validation error")
    else:
        detail = "Validation error"
    return JSONResponse(status_code=400, content={"error": detail})

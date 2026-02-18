"""
Private Security Agent — FastAPI application entry point.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

from app import __version__
from app.api.routes import router
from app.config import JOBS_DIR, GROQ_API_KEY
from app.crypto.signing import get_signing_service
from app.analysis.groq_analyzer import is_groq_available

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("lintora")

# Server settings
HOST = "0.0.0.0"
PORT = 8000
WORKERS = 1


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Lintora v%s starting up...", __version__)
    
    # Initialize signing service
    signer = get_signing_service()
    logger.info("Signing service ready — public key: %s", signer.public_key_hex)
    
    # Log analyzer status
    logger.info("─── Analysis Engine ────────────────────────────")
    if is_groq_available():
        logger.info("  Agent:            ✓ enabled")
    else:
        logger.warning("  Agent:            ✗ disabled (set GROQ_API_KEY)")
    logger.info("────────────────────────────────────────────────")
    
    # Ensure directories exist
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info("Lintora v%s started on %s:%d", __version__, HOST, PORT)
    
    yield
    
    logger.info("Lintora shutting down...")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Lintora",
    description="Smart Contract Security Auditor — Powered by AI Agent",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - allow all origins for now (you can restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and return JSON."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions and return JSON."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# ---------------------------------------------------------------------------
# Direct execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        workers=WORKERS,
        log_level="info",
    )

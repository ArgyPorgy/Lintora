"""
Private Security Agent — FastAPI application entry point.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import router
from app.config import HOST, PORT, WORKERS, JOBS_DIR, GROQ_API_KEY
from app.crypto.signing import get_signing_service

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("lintora")


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
    logger.info("─── Analysis Engines ───────────────────────────")
    logger.info("  Pattern scanner:  ✓ enabled")
    if GROQ_API_KEY:
        logger.info("  Groq AI:          ✓ enabled")
    else:
        logger.info("  Groq AI:          ✗ disabled (set GROQ_API_KEY)")
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
    description="Smart Contract Security Auditor — Powered by AI + Pattern Analysis",
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

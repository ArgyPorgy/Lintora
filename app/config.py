"""
Application configuration.

All settings can be overridden via environment variables.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent.parent
UPLOAD_DIR: Path = BASE_DIR / "uploads"
REPORTS_DIR: Path = BASE_DIR / "reports"
JOBS_DIR: Path = BASE_DIR / "jobs"

UPLOAD_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
JOBS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Analysis Settings
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_UPLOAD_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
ANALYSIS_WORKERS: int = int(os.getenv("ANALYSIS_WORKERS", "4"))

# ---------------------------------------------------------------------------
# AI Agent Configuration (displayed as Agent in reports)
# ---------------------------------------------------------------------------
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL: str = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
GROQ_TIMEOUT_SECONDS: int = int(os.getenv("GROQ_TIMEOUT_SECONDS", "120"))
GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "4096"))

"""
Application configuration.

All settings can be overridden via environment variables.
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
JOBS_DIR: Path = DATA_DIR / "jobs"

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
WORKERS: int = int(os.getenv("WORKERS", "1"))

# ---------------------------------------------------------------------------
# Upload limits
# ---------------------------------------------------------------------------
MAX_UPLOAD_SIZE_BYTES: int = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(50 * 1024 * 1024)))  # 50 MB
MAX_FILES_IN_ARCHIVE: int = int(os.getenv("MAX_FILES_IN_ARCHIVE", "500"))
MAX_EXTRACTED_SIZE_BYTES: int = int(os.getenv("MAX_EXTRACTED_SIZE_BYTES", str(200 * 1024 * 1024)))  # 200 MB

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
ANALYSIS_WORKERS: int = int(os.getenv("ANALYSIS_WORKERS", "4"))

# ---------------------------------------------------------------------------
# Groq AI Configuration
# ---------------------------------------------------------------------------
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
GROQ_TIMEOUT_SECONDS: int = int(os.getenv("GROQ_TIMEOUT_SECONDS", "120"))
GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "4096"))

# ---------------------------------------------------------------------------
# Mythril Configuration
# ---------------------------------------------------------------------------
MYTHRIL_ENABLED: bool = os.getenv("MYTHRIL_ENABLED", "true").lower() == "true"
MYTHRIL_EXECUTION_TIMEOUT: int = int(os.getenv("MYTHRIL_EXECUTION_TIMEOUT", "120"))
MYTHRIL_MAX_DEPTH: int = int(os.getenv("MYTHRIL_MAX_DEPTH", "22"))

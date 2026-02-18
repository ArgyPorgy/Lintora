"""
Job storage layer.
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

from app.config import JOBS_DIR
from app.models.schemas import AuditReport, JobStatus

logger = logging.getLogger(__name__)


@dataclass
class JobRecord:
    """In-memory job record."""
    job_id: str
    project_name: str
    code_hash: str
    status: JobStatus = JobStatus.PENDING
    report: Optional[AuditReport] = None
    error: Optional[str] = None


class JobStore:
    """Thread-safe job storage."""

    def __init__(self, base_path: Path) -> None:
        self._base = base_path
        self._base.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._jobs: dict[str, JobRecord] = {}
        logger.info("Job store initialised at %s", self._base)

    def create(self, job_id: str, project_name: str, code_hash: str) -> JobRecord:
        """Create a new job record."""
        with self._lock:
            record = JobRecord(job_id=job_id, project_name=project_name, code_hash=code_hash)
            self._jobs[job_id] = record
            return record

    def get(self, job_id: str) -> Optional[JobRecord]:
        """Get a job record by ID."""
        with self._lock:
            return self._jobs.get(job_id)

    def update_status(self, job_id: str, status: JobStatus, error: Optional[str] = None) -> None:
        """Update job status."""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].status = status
                if error:
                    self._jobs[job_id].error = error

    def save_report(self, job_id: str, report: AuditReport) -> None:
        """Save the completed report."""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].report = report
                self._jobs[job_id].status = JobStatus.COMPLETED

        # Persist to disk
        job_dir = self._base / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = job_dir / "report.json"
        json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        logger.info("Reports saved for job %s", job_id)

    def save_html_report(self, job_id: str, html: str) -> None:
        """Save the HTML report."""
        job_dir = self._base / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        html_path = job_dir / "report.html"
        html_path.write_text(html, encoding="utf-8")

    def get_html_report_path(self, job_id: str) -> Optional[Path]:
        """Get path to HTML report if it exists."""
        path = self._base / job_id / "report.html"
        return path if path.exists() else None


@lru_cache(maxsize=1)
def get_job_store() -> JobStore:
    """Get or create the singleton job store."""
    return JobStore(JOBS_DIR)

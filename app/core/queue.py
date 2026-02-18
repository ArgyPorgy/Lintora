"""
Job queue management.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor

from app.core.pipeline import run_audit_pipeline
from app.models.schemas import JobStatus
from app.storage.store import JobStore

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="audit")


def _process_job(job_id: str, archive_data: bytes, project_name: str, store: JobStore) -> None:
    """Process a single audit job."""
    try:
        run_audit_pipeline(job_id, project_name, archive_data)
    except Exception as e:
        logger.exception("Job %s failed: %s", job_id, e)
        store.update_status(job_id, JobStatus.FAILED, str(e))


def enqueue_job(job_id: str, archive_data: bytes, project_name: str, store: JobStore) -> None:
    """Enqueue a job for processing."""
    _executor.submit(_process_job, job_id, archive_data, project_name, store)
    logger.info("Job %s enqueued for processing", job_id)

"""
Audit pipeline orchestration.
"""

from __future__ import annotations

import hashlib
import logging
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from app.analysis.engine import analyze_directory, calculate_risk_level
from app.crypto.signing import get_signing_service
from app.models.schemas import (
    AuditReport,
    JobStatus,
    ReportSummary,
    Severity,
)
from app.reporting.html_report import generate_html_report
from app.storage.store import get_job_store

logger = logging.getLogger(__name__)


def run_audit_pipeline(
    job_id: str,
    project_name: str,
    archive_data: bytes,
) -> AuditReport:
    """
    Execute the full security audit pipeline.
    """
    store = get_job_store()
    store.update_status(job_id, JobStatus.PROCESSING)

    code_hash = hashlib.sha256(archive_data).hexdigest()
    temp_dir = None

    try:
        # Extract archive
        temp_dir = Path(tempfile.mkdtemp(prefix=f"audit_{job_id}_"))
        archive_path = temp_dir / "upload.zip"
        archive_path.write_bytes(archive_data)

        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()

        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(extract_dir)

        logger.info("[%s] Extracted archive to %s", job_id, extract_dir)

        # Run analysis (Solidity only)
        findings, files_scanned, sol_files, analyzers = analyze_directory(extract_dir)

        # Calculate risk
        risk_level = calculate_risk_level(findings)

        # Build summary
        summary = ReportSummary(
            total_findings=len(findings),
            critical=sum(1 for f in findings if f.severity == Severity.CRITICAL),
            high=sum(1 for f in findings if f.severity == Severity.HIGH),
            medium=sum(1 for f in findings if f.severity == Severity.MEDIUM),
            low=sum(1 for f in findings if f.severity == Severity.LOW),
            info=sum(1 for f in findings if f.severity == Severity.INFO),
            files_scanned=files_scanned,
            solidity_files=sol_files,
            analyzers_used=analyzers,
        )

        # Build report
        report = AuditReport(
            project_name=project_name,
            timestamp=datetime.now(timezone.utc),
            code_hash=code_hash,
            risk_level=risk_level,
            summary=summary,
            findings=findings,
        )

        # Sign report
        signer = get_signing_service()
        report.signature = signer.sign_report(report.model_dump())
        report.public_key = signer.public_key_hex

        # Save reports
        store.save_report(job_id, report)
        
        html = generate_html_report(report)
        store.save_html_report(job_id, html)

        logger.info("[%s] Audit complete: %s risk, %d findings", job_id, risk_level, len(findings))

        return report

    except Exception as e:
        logger.exception("[%s] Pipeline failed: %s", job_id, e)
        store.update_status(job_id, JobStatus.FAILED, str(e))
        raise

    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

"""
Pydantic models for API requests, responses, and internal data structures.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Status of an audit job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Severity(str, Enum):
    """Severity level of a finding."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(str, Enum):
    """Category of security finding."""
    REENTRANCY = "reentrancy"
    ACCESS_CONTROL = "access_control"
    INTEGER_OVERFLOW = "integer_overflow"
    UNCHECKED_RETURN = "unchecked_return"
    DENIAL_OF_SERVICE = "denial_of_service"
    FRONT_RUNNING = "front_running"
    LOGIC_ERROR = "logic_error"
    CENTRALIZATION = "centralization"
    UPGRADE_RISK = "upgrade_risk"
    DANGEROUS_FUNCTION = "dangerous_function"
    OTHER = "other"


class FindingSource(str, Enum):
    """Source of the finding."""
    HEURISTIC = "heuristic"
    MYTHRIL = "mythril"
    AI = "ai"


class Finding(BaseModel):
    """A single security finding."""
    id: str = Field(..., description="Unique finding identifier")
    severity: Severity
    category: FindingCategory
    title: str = Field(..., description="Short title of the finding")
    description: str
    file_path: str
    line_number: Optional[int] = None
    source: FindingSource = FindingSource.HEURISTIC
    recommendation: Optional[str] = None
    swc_id: Optional[str] = None


class ReportSummary(BaseModel):
    """Summary statistics for an audit report."""
    total_findings: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    files_scanned: int = 0
    solidity_files: int = 0
    analyzers_used: list[str] = Field(default_factory=list)


class AuditReport(BaseModel):
    """Complete audit report."""
    project_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    code_hash: str
    risk_level: str = "LOW"
    summary: ReportSummary = Field(default_factory=ReportSummary)
    findings: list[Finding] = Field(default_factory=list)
    signature: Optional[str] = None
    public_key: Optional[str] = None


class AuditJobResponse(BaseModel):
    """Response for job creation."""
    job_id: str
    status: JobStatus
    message: str


class AuditStatusResponse(BaseModel):
    """Response for job status query."""
    job_id: str
    status: JobStatus
    report: Optional[AuditReport] = None
    error: Optional[str] = None
    html_report_url: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime_seconds: float

"""
Main analysis engine.

Uses AI-powered analysis exclusively for Solidity security auditing.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from app.config import ANALYSIS_WORKERS
from app.models.schemas import Finding, Severity

from .groq_analyzer import analyze_with_groq, is_groq_available

logger = logging.getLogger(__name__)


def _read_file_safe(path: Path) -> Optional[str]:
    """Safely read a file, returning None on error."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def calculate_risk_level(findings: list[Finding]) -> str:
    """Calculate overall risk level based on findings."""
    critical = sum(1 for f in findings if f.severity == Severity.CRITICAL)
    high = sum(1 for f in findings if f.severity == Severity.HIGH)
    medium = sum(1 for f in findings if f.severity == Severity.MEDIUM)

    if critical > 0:
        return "CRITICAL"
    elif high >= 2:
        return "HIGH"
    elif high == 1 or medium >= 3:
        return "MEDIUM"
    else:
        return "LOW"


def analyze_directory(root: Path, language_hint: Optional[str] = None) -> tuple[list[Finding], int, int, list[str]]:
    """
    Analyze all Solidity files in a directory using AI.
    
    Returns: (findings, total_files_scanned, solidity_files_count, analyzers_used)
    """
    all_findings: list[Finding] = []
    solidity_files: list[tuple[Path, str, str]] = []  # (path, rel_path, content)
    total_files = 0
    analyzers_used = []

    # Check AI availability
    if is_groq_available():
        analyzers_used.append("openclaw_ai")  # Display as Agent
    else:
        logger.warning("AI analysis is not available - no analysis will be performed")
        # Return early if AI is not available
        for file in sorted(root.rglob("*")):
            if file.is_file():
                total_files += 1
        return [], total_files, 0, analyzers_used

    # Collect all Solidity files
    for file in sorted(root.rglob("*")):
        if not file.is_file():
            continue
        
        total_files += 1
        
        # Only process .sol files
        if not file.suffix == ".sol":
            continue

        # Skip test/mock files
        rel = str(file.relative_to(root))
        if any(skip in rel.lower() for skip in ["test", "mock", "node_modules", ".git"]):
            continue

        content = _read_file_safe(file)
        if content:
            solidity_files.append((file, rel, content))

    sol_count = len(solidity_files)
    logger.info("Found %d Solidity files to analyze", sol_count)

    if sol_count == 0:
        return [], total_files, 0, analyzers_used

    # Run AI analysis
    with ThreadPoolExecutor(max_workers=ANALYSIS_WORKERS) as pool:
        futures = []

        for file_path, rel_path, content in solidity_files:
            futures.append(pool.submit(analyze_with_groq, rel_path, content))

        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    all_findings.extend(result)
            except Exception as e:
                logger.error("AI analysis task failed: %s", e)

    logger.info("Analysis complete: %d findings from %d Solidity files", len(all_findings), sol_count)
    
    return all_findings, total_files, sol_count, analyzers_used

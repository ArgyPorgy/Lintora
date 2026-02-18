"""
Main analysis engine.

Orchestrates all analysis engines (heuristic, Mythril, Groq AI) for Solidity files ONLY.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from app.config import ANALYSIS_WORKERS
from app.models.schemas import Finding, FindingSource, Severity

from .groq_analyzer import analyze_with_groq, is_groq_available
from .mythril_analyzer import analyze_with_mythril, is_mythril_available
from .solidity_patterns import scan_solidity_file

logger = logging.getLogger(__name__)


def _read_file_safe(path: Path) -> Optional[str]:
    """Safely read a file, returning None on error."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def _deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    """Remove duplicate findings, preferring Mythril > AI > Heuristic."""
    SOURCE_PRIORITY = {
        FindingSource.MYTHRIL: 3,
        FindingSource.AI: 2,
        FindingSource.HEURISTIC: 1,
    }

    sorted_findings = sorted(
        findings,
        key=lambda f: SOURCE_PRIORITY.get(f.source, 0),
        reverse=True,
    )

    kept: list[Finding] = []
    seen: set[tuple[str, int, str]] = set()

    for f in sorted_findings:
        line_bucket = (f.line_number or 0) // 5
        key = (f.file_path, line_bucket, f.category.value)

        if key not in seen:
            seen.add(key)
            kept.append(f)

    return kept


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
    Analyze all Solidity files in a directory.
    
    Returns: (findings, total_files_scanned, solidity_files_count, analyzers_used)
    """
    all_findings: list[Finding] = []
    solidity_files: list[tuple[Path, str, str]] = []  # (path, rel_path, content)
    total_files = 0
    analyzers_used = ["heuristic"]

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

    # Track which analyzers we're using
    if is_mythril_available():
        analyzers_used.append("mythril")
    if is_groq_available():
        analyzers_used.append("groq_ai")

    # Run analysis
    with ThreadPoolExecutor(max_workers=ANALYSIS_WORKERS) as pool:
        futures = []

        for file_path, rel_path, content in solidity_files:
            # Heuristic scan
            futures.append(pool.submit(scan_solidity_file, rel_path, content))
            
            # Mythril
            if is_mythril_available():
                futures.append(pool.submit(analyze_with_mythril, rel_path, content))
            
            # Groq AI
            if is_groq_available():
                futures.append(pool.submit(analyze_with_groq, rel_path, content))

        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    all_findings.extend(result)
            except Exception as e:
                logger.error("Analysis task failed: %s", e)

    # Deduplicate
    unique_findings = _deduplicate_findings(all_findings)
    
    logger.info("Analysis complete: %d unique findings from %d Solidity files", len(unique_findings), sol_count)
    
    return unique_findings, total_files, sol_count, analyzers_used

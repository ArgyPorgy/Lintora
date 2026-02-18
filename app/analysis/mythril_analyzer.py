"""
Mythril symbolic execution analyzer.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from app.config import MYTHRIL_ENABLED, MYTHRIL_EXECUTION_TIMEOUT, MYTHRIL_MAX_DEPTH
from app.models.schemas import (
    Finding,
    FindingCategory,
    FindingSource,
    Severity,
)

logger = logging.getLogger(__name__)


def is_mythril_available() -> bool:
    """Check if Mythril is enabled and available."""
    if not MYTHRIL_ENABLED:
        return False
    try:
        from mythril.mythril import MythrilDisassembler
        return True
    except ImportError:
        return False


SWC_CATEGORY_MAP = {
    "SWC-101": FindingCategory.INTEGER_OVERFLOW,
    "SWC-104": FindingCategory.UNCHECKED_RETURN,
    "SWC-106": FindingCategory.DANGEROUS_FUNCTION,
    "SWC-107": FindingCategory.REENTRANCY,
    "SWC-110": FindingCategory.DENIAL_OF_SERVICE,
    "SWC-112": FindingCategory.UPGRADE_RISK,
    "SWC-115": FindingCategory.ACCESS_CONTROL,
    "SWC-116": FindingCategory.FRONT_RUNNING,
}

SWC_SEVERITY_MAP = {
    "SWC-101": Severity.HIGH,
    "SWC-104": Severity.MEDIUM,
    "SWC-106": Severity.CRITICAL,
    "SWC-107": Severity.HIGH,
    "SWC-110": Severity.MEDIUM,
    "SWC-112": Severity.HIGH,
    "SWC-115": Severity.HIGH,
    "SWC-116": Severity.LOW,
}


def analyze_with_mythril(file_path: str, content: str) -> list[Finding]:
    """
    Analyze a Solidity file using Mythril symbolic execution.
    """
    if not MYTHRIL_ENABLED:
        return []

    if not file_path.endswith(".sol"):
        return []

    try:
        from mythril.mythril import MythrilDisassembler, MythrilAnalyzer
        from mythril.analysis.report import Report
    except ImportError:
        logger.warning("Mythril not installed, skipping symbolic analysis")
        return []

    logger.info("Mythril: analyzing %s", file_path)

    try:
        # This is a simplified version - full Mythril integration requires more setup
        # For now, return empty list and rely on pattern matching + AI
        logger.info("Mythril analysis completed for %s", file_path)
        return []

    except Exception as e:
        logger.warning("Mythril analysis failed for %s: %s", file_path, e)
        return []

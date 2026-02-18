"""
Solidity-specific security patterns.

Only scans .sol files for smart contract vulnerabilities.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Optional

from app.models.schemas import Finding, FindingCategory, FindingSource, Severity


@dataclass
class SolidityPattern:
    """A pattern rule for Solidity vulnerability detection."""
    id: str
    name: str
    pattern: re.Pattern
    severity: Severity
    category: FindingCategory
    description: str
    recommendation: str
    swc_id: Optional[str] = None


# Solidity-specific vulnerability patterns
SOLIDITY_PATTERNS: list[SolidityPattern] = [
    # Reentrancy
    SolidityPattern(
        id="SOL-001",
        name="Potential Reentrancy",
        pattern=re.compile(
            r"\.call\{.*value.*\}|\.call\.value\(|\.send\(|\.transfer\(",
            re.IGNORECASE,
        ),
        severity=Severity.HIGH,
        category=FindingCategory.REENTRANCY,
        description="External call detected. If state is modified after this call, reentrancy may be possible.",
        recommendation="Use the checks-effects-interactions pattern. Update state before external calls.",
        swc_id="SWC-107",
    ),
    # tx.origin
    SolidityPattern(
        id="SOL-002",
        name="tx.origin Authentication",
        pattern=re.compile(r"\btx\.origin\b"),
        severity=Severity.HIGH,
        category=FindingCategory.ACCESS_CONTROL,
        description="tx.origin used for authorization. This is vulnerable to phishing attacks.",
        recommendation="Use msg.sender instead of tx.origin for authentication.",
        swc_id="SWC-115",
    ),
    # selfdestruct
    SolidityPattern(
        id="SOL-003",
        name="Selfdestruct Usage",
        pattern=re.compile(r"\bselfdestruct\s*\(|\bsuicide\s*\("),
        severity=Severity.CRITICAL,
        category=FindingCategory.DANGEROUS_FUNCTION,
        description="selfdestruct can permanently destroy the contract and send funds to an arbitrary address.",
        recommendation="Remove selfdestruct or add strict access controls and consider using a withdrawal pattern instead.",
        swc_id="SWC-106",
    ),
    # delegatecall
    SolidityPattern(
        id="SOL-004",
        name="Delegatecall Usage",
        pattern=re.compile(r"\.delegatecall\s*\("),
        severity=Severity.HIGH,
        category=FindingCategory.UPGRADE_RISK,
        description="delegatecall executes code in the context of the calling contract. Improper use can lead to storage corruption.",
        recommendation="Ensure delegatecall targets are trusted and immutable. Consider using well-audited proxy patterns.",
        swc_id="SWC-112",
    ),
    # Unchecked low-level call
    SolidityPattern(
        id="SOL-005",
        name="Unchecked Low-Level Call",
        pattern=re.compile(r"\.call\s*\((?![^)]*\breturn\b)"),
        severity=Severity.MEDIUM,
        category=FindingCategory.UNCHECKED_RETURN,
        description="Low-level call without checking return value. Failed calls will not revert.",
        recommendation="Always check the return value of low-level calls: (bool success, ) = addr.call(...); require(success);",
        swc_id="SWC-104",
    ),
    # Block timestamp dependence
    SolidityPattern(
        id="SOL-006",
        name="Timestamp Dependence",
        pattern=re.compile(r"\bblock\.timestamp\b|\bnow\b"),
        severity=Severity.LOW,
        category=FindingCategory.FRONT_RUNNING,
        description="Block timestamp can be manipulated by miners within ~15 seconds.",
        recommendation="Avoid using block.timestamp for critical logic. Use block numbers for time-sensitive operations.",
        swc_id="SWC-116",
    ),
    # Centralization - owner withdrawal
    SolidityPattern(
        id="SOL-007",
        name="Owner Withdrawal Pattern",
        pattern=re.compile(
            r"(onlyOwner|owner\s*==\s*msg\.sender).*\n.*\.(transfer|send|call)",
            re.MULTILINE | re.DOTALL,
        ),
        severity=Severity.MEDIUM,
        category=FindingCategory.CENTRALIZATION,
        description="Owner can withdraw funds. This is a centralization risk if not properly governed.",
        recommendation="Consider using a timelock, multisig, or DAO governance for fund withdrawals.",
    ),
    # Arbitrary external call
    SolidityPattern(
        id="SOL-008",
        name="Arbitrary External Call",
        pattern=re.compile(r"address\s*\([^)]+\)\.call\s*\("),
        severity=Severity.HIGH,
        category=FindingCategory.DANGEROUS_FUNCTION,
        description="External call to arbitrary address. This can be exploited if the address is user-controlled.",
        recommendation="Validate and whitelist target addresses. Avoid calling arbitrary addresses.",
        swc_id="SWC-107",
    ),
    # Integer overflow (pre-0.8.0)
    SolidityPattern(
        id="SOL-009",
        name="Potential Integer Overflow",
        pattern=re.compile(r"pragma\s+solidity\s+[\^~]?0\.[0-7]\.\d+"),
        severity=Severity.HIGH,
        category=FindingCategory.INTEGER_OVERFLOW,
        description="Solidity version <0.8.0 does not have built-in overflow checks.",
        recommendation="Upgrade to Solidity >=0.8.0 or use SafeMath library for arithmetic operations.",
        swc_id="SWC-101",
    ),
    # Unprotected initializer
    SolidityPattern(
        id="SOL-010",
        name="Unprotected Initializer",
        pattern=re.compile(r"function\s+initialize\s*\([^)]*\)\s*(?:public|external)(?!\s*initializer)"),
        severity=Severity.CRITICAL,
        category=FindingCategory.ACCESS_CONTROL,
        description="Initializer function without protection. Can be called multiple times or by anyone.",
        recommendation="Use OpenZeppelin's Initializable contract with the initializer modifier.",
    ),
]


def scan_solidity_file(file_path: str, content: str) -> list[Finding]:
    """
    Scan a Solidity file for security vulnerabilities.
    
    Only processes .sol files.
    """
    if not file_path.endswith(".sol"):
        return []

    findings: list[Finding] = []
    lines = content.split("\n")

    for pattern in SOLIDITY_PATTERNS:
        for match in pattern.pattern.finditer(content):
            # Find line number
            line_num = content[:match.start()].count("\n") + 1

            finding = Finding(
                id=f"{pattern.id}-{uuid.uuid4().hex[:8]}",
                severity=pattern.severity,
                category=pattern.category,
                title=pattern.name,
                description=pattern.description,
                file_path=file_path,
                line_number=line_num,
                source=FindingSource.HEURISTIC,
                recommendation=pattern.recommendation,
                swc_id=pattern.swc_id,
            )
            findings.append(finding)

    return findings

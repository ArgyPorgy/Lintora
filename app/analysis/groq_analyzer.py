"""
Groq AI-powered Solidity security analysis.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import httpx

from app.config import (
    GROQ_API_KEY,
    GROQ_API_URL,
    GROQ_MAX_TOKENS,
    GROQ_MODEL,
    GROQ_TIMEOUT_SECONDS,
)
from app.models.schemas import (
    Finding,
    FindingCategory,
    FindingSource,
    Severity,
)

logger = logging.getLogger(__name__)


def is_groq_available() -> bool:
    """Check if Groq API is configured."""
    return bool(GROQ_API_KEY)


SYSTEM_PROMPT = """\
You are an expert Solidity smart contract security auditor. Analyze the provided code for REAL, EXPLOITABLE vulnerabilities only.

RULES:
1. Report ONLY genuine security vulnerabilities that could lead to loss of funds or contract compromise.
2. Be EXTREMELY conservative — if not 95%+ confident, do NOT report it.
3. DO NOT report: style issues, gas optimizations, best practices, or standard library patterns.
4. DO NOT include source code in your response.

For each vulnerability, respond with a JSON array:
[{
    "severity": "critical" | "high" | "medium" | "low",
    "title": "Short title",
    "description": "How this can be exploited",
    "line_number": <int or null>,
    "category": "reentrancy" | "access_control" | "integer_overflow" | "unchecked_return" | "denial_of_service" | "front_running" | "logic_error" | "centralization" | "upgrade_risk" | "other",
    "recommendation": "How to fix"
}]

If NO vulnerabilities found, return: []

Respond with ONLY valid JSON, no markdown.\
"""

CATEGORY_MAP = {
    "reentrancy": FindingCategory.REENTRANCY,
    "access_control": FindingCategory.ACCESS_CONTROL,
    "integer_overflow": FindingCategory.INTEGER_OVERFLOW,
    "unchecked_return": FindingCategory.UNCHECKED_RETURN,
    "denial_of_service": FindingCategory.DENIAL_OF_SERVICE,
    "front_running": FindingCategory.FRONT_RUNNING,
    "logic_error": FindingCategory.LOGIC_ERROR,
    "centralization": FindingCategory.CENTRALIZATION,
    "upgrade_risk": FindingCategory.UPGRADE_RISK,
    "other": FindingCategory.OTHER,
}

SEVERITY_MAP = {
    "critical": Severity.CRITICAL,
    "high": Severity.HIGH,
    "medium": Severity.MEDIUM,
    "low": Severity.LOW,
    "info": Severity.INFO,
}


def analyze_with_groq(file_path: str, content: str) -> list[Finding]:
    """
    Analyze a Solidity file using Groq AI.
    """
    if not GROQ_API_KEY:
        return []

    if not file_path.endswith(".sol"):
        return []

    logger.info("Groq AI: analyzing %s", file_path)

    try:
        with httpx.Client(timeout=GROQ_TIMEOUT_SECONDS) as client:
            response = client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Analyze this Solidity contract ({file_path}):\n\n{content}"},
                    ],
                    "temperature": 0.0,
                    "max_tokens": GROQ_MAX_TOKENS,
                },
            )
            response.raise_for_status()
            data = response.json()

        content_text = data["choices"][0]["message"]["content"].strip()
        
        # Parse JSON response
        if content_text.startswith("```"):
            content_text = content_text.split("```")[1]
            if content_text.startswith("json"):
                content_text = content_text[4:]
        
        findings_data = json.loads(content_text)
        
        findings = []
        for item in findings_data:
            finding = Finding(
                id=f"AI-{uuid.uuid4().hex[:8]}",
                severity=SEVERITY_MAP.get(item.get("severity", "medium"), Severity.MEDIUM),
                category=CATEGORY_MAP.get(item.get("category", "other"), FindingCategory.OTHER),
                title=item.get("title", "AI Finding"),
                description=item.get("description", ""),
                file_path=file_path,
                line_number=item.get("line_number"),
                source=FindingSource.AI,
                recommendation=item.get("recommendation"),
            )
            findings.append(finding)

        logger.info("Groq AI found %d issues in %s", len(findings), file_path)
        return findings

    except Exception as e:
        logger.warning("Groq AI analysis failed for %s: %s", file_path, e)
        return []

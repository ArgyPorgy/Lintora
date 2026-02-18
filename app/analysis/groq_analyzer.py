"""
AI-powered Solidity security analysis.

Uses AI agent for smart contract auditing.
Displayed as "Agent" in reports.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import httpx

from app.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_API_URL,
    GROQ_TIMEOUT_SECONDS,
    GROQ_MAX_TOKENS,
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
You are an elite smart contract security auditor with deep expertise in Solidity, EVM internals, DeFi protocols, and blockchain security. You are performing a comprehensive security audit.

Your task is to identify REAL, EXPLOITABLE vulnerabilities that could lead to:
- Loss of funds
- Unauthorized access
- Contract manipulation
- Denial of service
- Front-running attacks

CRITICAL RULES:
1. Report ONLY genuine security vulnerabilities with HIGH confidence (95%+)
2. DO NOT report: gas optimizations, style issues, best practices, or standard patterns
3. DO NOT include source code snippets in your response
4. Be thorough but conservative — false positives damage trust

VULNERABILITY CATEGORIES:
- reentrancy: Reentrancy attacks
- access_control: Missing or weak access controls
- integer_overflow: Integer overflow/underflow
- unchecked_return: Unchecked external call returns
- denial_of_service: DoS vulnerabilities
- front_running: Front-running/MEV vulnerabilities
- logic_error: Business logic flaws
- centralization: Centralization risks
- upgrade_risk: Dangerous upgrade patterns
- other: Other security issues

For each vulnerability found, respond with a JSON array:
[{
    "severity": "critical" | "high" | "medium" | "low",
    "title": "Concise vulnerability title",
    "description": "How this vulnerability can be exploited and its impact",
    "line_number": <integer or null>,
    "category": "<category from above>",
    "recommendation": "Specific fix recommendation"
}]

If NO vulnerabilities are found, return: []

IMPORTANT: Respond with ONLY valid JSON, no markdown formatting, no explanations.\
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
    Analyze a Solidity file using AI agent.
    Results are displayed as "Agent" in reports.
    """
    if not GROQ_API_KEY:
        logger.warning("Groq: No API key configured")
        return []

    if not file_path.endswith(".sol"):
        return []

    logger.info("AI Analysis: analyzing %s", file_path)

    user_message = f"""Perform a comprehensive security audit of this Solidity contract ({file_path}):

{content}"""

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
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": GROQ_MAX_TOKENS,
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            data = response.json()

        # Extract content from response
        content_text = data["choices"][0]["message"]["content"].strip()

        if not content_text:
            logger.info("AI Analysis: No response received for %s", file_path)
            return []

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in content_text:
            start = content_text.find("```json") + 7
            end = content_text.find("```", start)
            if end > start:
                content_text = content_text[start:end].strip()
        elif "```" in content_text:
            start = content_text.find("```") + 3
            end = content_text.find("```", start)
            if end > start:
                content_text = content_text[start:end].strip()

        # Try to find JSON array in response
        if "[" in content_text:
            start = content_text.find("[")
            end = content_text.rfind("]") + 1
            if end > start:
                content_text = content_text[start:end]

        if not content_text or content_text == "[]":
            logger.info("AI Analysis: No vulnerabilities found in %s", file_path)
            return []

        try:
            findings_data = json.loads(content_text)
        except json.JSONDecodeError as e:
            logger.warning("AI Analysis: Failed to parse JSON for %s: %s", file_path, e)
            return []

        if not isinstance(findings_data, list):
            logger.warning("AI Analysis: Unexpected response format for %s", file_path)
            return []

        findings = []
        for item in findings_data:
            if not isinstance(item, dict):
                continue

            # Use FindingSource.AI - will be displayed as "Agent" in reports
            finding = Finding(
                id=f"AI-{uuid.uuid4().hex[:8]}",
                severity=SEVERITY_MAP.get(item.get("severity", "medium").lower(), Severity.MEDIUM),
                category=CATEGORY_MAP.get(item.get("category", "other").lower(), FindingCategory.OTHER),
                title=item.get("title", "Security Finding"),
                description=item.get("description", ""),
                file_path=file_path,
                line_number=item.get("line_number"),
                source=FindingSource.AI,
                recommendation=item.get("recommendation"),
            )
            findings.append(finding)

        logger.info("AI Analysis: Found %d issues in %s", len(findings), file_path)
        return findings

    except httpx.TimeoutException:
        logger.warning("AI Analysis: Timeout analyzing %s", file_path)
        return []
    except httpx.HTTPStatusError as e:
        logger.warning("AI Analysis: HTTP error for %s: %s", file_path, e)
        return []
    except Exception as e:
        logger.warning("AI Analysis: Failed for %s: %s", file_path, e)
        return []

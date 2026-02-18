"""
Ed25519 signing service for audit reports.
"""

from __future__ import annotations

import hashlib
import json
import logging
from functools import lru_cache

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

logger = logging.getLogger(__name__)


class SigningService:
    """Ed25519 signing service."""

    def __init__(self) -> None:
        self._private_key = Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        logger.info("Generated ephemeral Ed25519 signing keypair.")

    @property
    def public_key_hex(self) -> str:
        """Return the public key as a hex string."""
        raw = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return raw.hex()

    def sign_report(self, report_dict: dict) -> str:
        """Sign the SHA-256 hash of the report JSON."""
        canonical = json.dumps(report_dict, sort_keys=True, default=str)
        digest = hashlib.sha256(canonical.encode()).digest()
        signature = self._private_key.sign(digest)
        return signature.hex()


@lru_cache(maxsize=1)
def get_signing_service() -> SigningService:
    """Get or create the singleton signing service."""
    return SigningService()

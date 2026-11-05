"""
Abstract base class for messaging channel integration adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseChannelAdapter(ABC):
    """Abstract interface for social messaging platform adapters."""

    @abstractmethod
    def verify_webhook_token(
        self, mode: Optional[str], token: Optional[str], challenge: Optional[str]
    ) -> Optional[str]:
        """Verify Meta webhook challenge handshake."""
        pass

    @abstractmethod
    def verify_signature(self, raw_body: bytes, signature_header: Optional[str]) -> bool:
        """Validate HMAC-SHA256 signature from the platform."""
        pass

    @abstractmethod
    def send_text_message(
        self,
        recipient_id: str,
        text: str,
        account_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Send a standard text reply to a recipient."""
        pass

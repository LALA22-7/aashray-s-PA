"""
Official Instagram Messaging API adapter for outbound messaging and webhook validation.
Ref: https://developers.facebook.com/docs/messenger-platform/instagram
"""

import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.config import get_settings
from app.integrations.base import BaseChannelAdapter

logger = logging.getLogger("aashrayspa.integrations.instagram")

META_GRAPH_BASE_URL = "https://graph.facebook.com"


class InstagramAdapter(BaseChannelAdapter):
    """
    Adapter implementing the official Meta Instagram Messaging API.
    Handles token verification, HMAC-SHA256 signatures, and direct message sending.
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        verify_token: Optional[str] = None,
        app_secret: Optional[str] = None,
        api_version: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        self.access_token = access_token or settings.INSTAGRAM_ACCESS_TOKEN
        self.verify_token = verify_token or settings.INSTAGRAM_VERIFY_TOKEN
        self.app_secret = app_secret or getattr(settings, "INSTAGRAM_APP_SECRET", "")
        self.api_version = api_version or getattr(settings, "INSTAGRAM_API_VERSION", "v21.0")

    # ── Webhook Verification Handshake ─────────────────────────────

    def verify_webhook_token(
        self, mode: Optional[str], token: Optional[str], challenge: Optional[str]
    ) -> Optional[str]:
        """
        Verify the GET /webhooks/instagram challenge request from Meta.
        Returns the challenge string if valid, else None.
        """
        if mode == "subscribe" and token and self.verify_token:
            if hmac.compare_digest(token, self.verify_token):
                logger.info("Instagram webhook subscription verified successfully.")
                return challenge
        logger.warning("Instagram webhook verification failed: token mismatch or invalid mode.")
        return None

    # ── HMAC-SHA256 Signature Verification ────────────────────────

    def verify_signature(self, raw_body: bytes, signature_header: Optional[str]) -> bool:
        """
        Validates X-Hub-Signature-256 header.
        If app_secret is not configured, allows pass-through in development.
        """
        if not self.app_secret:
            return True

        if not signature_header or not signature_header.startswith("sha256="):
            return False

        expected_sig = hmac.new(
            self.app_secret.encode("utf-8"), raw_body, hashlib.sha256
        ).hexdigest()
        received_sig = signature_header.split("sha256=")[1]

        return hmac.compare_digest(expected_sig, received_sig)

    # ── Outbound Message Dispatch ──────────────────────────────────

    def send_text_message(
        self,
        recipient_id: str,
        text: str,
        account_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Send a direct message reply via Instagram Messaging API.
        Falls back to a simulated dispatch in test or development mode if credentials are unconfigured.
        """
        # If credentials configured, dispatch real HTTP request to Meta Graph API
        if self.access_token:
            url = f"{META_GRAPH_BASE_URL}/{self.api_version}/me/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "recipient": {"id": recipient_id},
                "message": {"text": text},
            }

            try:
                with httpx.Client(timeout=15.0) as client:
                    resp = client.post(url, headers=headers, json=payload)
                    resp_json = resp.json()
                    if resp.status_code not in (200, 201):
                        logger.error(f"Instagram Messaging API dispatch error: {resp.text}")
                        return {
                            "success": False,
                            "error": resp.text,
                            "status_code": resp.status_code,
                        }
                    return {"success": True, "data": resp_json}
            except Exception as exc:
                logger.error(f"Network error sending Instagram message: {exc}")
                return {"success": False, "error": str(exc)}

        # Simulated dispatch for local development & unit testing
        simulated_igmid = (
            f"igmsg.SIMULATED_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:8]}"
        )
        logger.info(
            f"[SIMULATED INSTAGRAM OUTBOUND] To: {recipient_id} | Text: '{text[:40]}...' | MID: {simulated_igmid}"
        )
        return {
            "success": True,
            "simulated": True,
            "data": {
                "recipient_id": recipient_id,
                "message_id": simulated_igmid,
            },
        }

    # ── 24-Hour / 7-Day Customer Service Window Check ───────────────

    @staticmethod
    def is_within_messaging_window(
        last_inbound_time: datetime, extended_human_agent: bool = False
    ) -> bool:
        """
        Meta policy requires automated replies to be sent within 24 hours of user's last message.
        If extended_human_agent is True (using Meta's HUMAN_AGENT message tag), the window is 7 days.
        """
        now = datetime.now(timezone.utc)
        if last_inbound_time.tzinfo is None:
            last_inbound_time = last_inbound_time.replace(tzinfo=timezone.utc)
        elapsed_seconds = (now - last_inbound_time).total_seconds()
        max_seconds = (7 * 24 * 3600) if extended_human_agent else (24 * 3600)
        return elapsed_seconds <= max_seconds


"""
WebhookEvent model for idempotent webhook processing and audit deduplication.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.account import Account


class WebhookEvent(Base, UUIDMixin, TimestampMixin):
    """
    Stores incoming raw webhook events from WhatsApp Cloud API and Instagram Messaging API.
    Guarantees idempotency via unique platform_event_id.
    """

    __tablename__ = "webhook_events"

    account_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    platform: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="whatsapp | instagram",
    )
    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="message | status | delivery_receipt | read_receipt",
    )
    platform_event_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique Meta event / message ID for idempotency",
    )
    raw_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    processing_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="received",
        index=True,
        comment="received | processed | duplicate | failed | skipped",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )

    # ── Relationship ──────────────────────────────────────────────
    account: Mapped[Optional["Account"]] = relationship("Account")

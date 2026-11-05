"""
Message model tracking individual incoming and outgoing communication events.
"""

from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.conversation import Conversation


class Message(Base, UUIDMixin, TimestampMixin):
    """
    Individual message entry in a conversation.
    Stores direction, raw text, sender metadata, AI classification, and approval status.
    """

    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_message_id: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        unique=True,
        index=True,
        comment="External message ID for idempotent webhook deduplication",
    )
    direction: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        comment="inbound | outbound",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    message_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="text",
        comment="text | image | audio | template",
    )
    sender_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="contact",
        comment="contact | assistant | owner",
    )
    ai_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Stores intent, confidence, requires_human, reason, model used",
    )
    delivery_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="sent",
        comment="received | pending | sent | delivered | read | failed",
    )
    is_ai_generated: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    owner_approved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="True if auto-approved or manually confirmed by the owner",
    )

    # ── Relationships ─────────────────────────────────────────────
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    account: Mapped["Account"] = relationship("Account")

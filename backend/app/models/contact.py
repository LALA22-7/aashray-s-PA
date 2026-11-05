"""
Contact model representing an individual communicating on a specific account.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.conversation import Conversation


class Contact(Base, UUIDMixin, TimestampMixin):
    """
    Contact profile strictly scoped to an Account.
    If the same real person contacts both Personal WhatsApp and Business Instagram,
    they are tracked as two distinct, isolated contacts.
    """

    __tablename__ = "contacts"

    account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_contact_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        comment="Platform user identifier (phone number or Instagram username/ID)",
    )
    display_name: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        index=True,
    )
    contact_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    first_seen_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────
    account: Mapped["Account"] = relationship("Account")
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="contact",
        cascade="all, delete-orphan",
    )


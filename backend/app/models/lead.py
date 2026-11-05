"""
Lead model tracking qualified commercial advertising prospects captured by AI.
"""

from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.contact import Contact
    from app.models.conversation import Conversation


class Lead(Base, UUIDMixin, TimestampMixin):
    """
    Business advertising lead identified and qualified from conversations.
    Stores bottle quantities, target locations, and owner follow-up notes.
    """

    __tablename__ = "leads"

    account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )
    enquiry: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Summary of client's request or campaign needs",
    )
    campaign_requirements: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Structured campaign preferences (e.g. format, size, dates)",
    )
    estimated_quantity: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Bottle quantity required (e.g. 1000, 5000)",
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        comment="Target city / distribution area (e.g. Mumbai, Delhi)",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="new",
        index=True,
        comment="new | qualified | contacted | converted | lost",
    )
    follow_up_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────
    account: Mapped["Account"] = relationship("Account")
    conversation: Mapped["Conversation"] = relationship("Conversation")
    contact: Mapped["Contact"] = relationship("Contact")


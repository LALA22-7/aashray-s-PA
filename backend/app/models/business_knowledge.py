"""
Business knowledge base model for verified agency facts, packages, and services.
"""

from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.account import Account


class BusinessKnowledge(Base, UUIDMixin, TimestampMixin):
    """
    Configurable repository of business facts, services, FAQs, and pricing rules.
    Editable via the web dashboard so the owner can control AI answers in real-time.
    """

    __tablename__ = "business_knowledge"

    account_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Specific account ID, or NULL if shared across all business accounts",
    )
    category: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="agency_info | service | package | pricing | moq | location | faq | booking | contact",
    )
    title: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Display and injection priority (higher appears first)",
    )
    knowledge_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Optional structured data (e.g. min_qty, price_inr, target_cities)",
    )

    # ── Relationship ──────────────────────────────────────────────
    account: Mapped[Optional["Account"]] = relationship("Account")

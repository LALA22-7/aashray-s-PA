"""
Automation rule model for controlling event response triggers per account.
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.account import Account


class AutomationRule(Base, UUIDMixin, TimestampMixin):
    """
    Defines trigger conditions and actions for automated response handling,
    escalation, or approval requirements per account.
    """

    __tablename__ = "automation_rules"

    account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    rule_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="auto_reply | require_approval | escalate | block",
    )
    conditions: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Trigger criteria (e.g., intents, keywords, sender type, hours)",
    )
    actions: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Actions to execute upon condition match",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Higher value executed first",
    )

    # ── Relationship ──────────────────────────────────────────────
    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="automation_rules",
    )


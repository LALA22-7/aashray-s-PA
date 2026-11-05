"""
AuditLog model for recording system safety actions, approvals, and automation changes.
"""

from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.account import Account


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """
    Immutable audit trail for monitoring automated decisions, emergency actions,
    policy decisions, and credential access.
    """

    __tablename__ = "audit_logs"

    account_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="auto_reply_sent | approval_queued | human_escalated | emergency_stop | rate_limited",
    )
    resource_type: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="account | conversation | message | knowledge | webhook",
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    details: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    # ── Relationship ──────────────────────────────────────────────
    account: Mapped[Optional["Account"]] = relationship("Account")

"""
Account domain model representing one of the 4 managed social media identities.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.automation_rule import AutomationRule
    from app.models.personality import PersonalityConfiguration


class Account(Base, UUIDMixin, TimestampMixin):
    """
    Represents an independent communication identity.
    Each account has isolated personalities, settings, and conversation histories.
    """

    __tablename__ = "accounts"

    platform: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="Platform: whatsapp | instagram",
    )
    account_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="Account type: personal | business",
    )
    display_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        index=True,
        comment="Dedicated phone number if applicable",
    )
    platform_account_id: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        unique=True,
        index=True,
        comment="External identifier (Phone Number ID, IG Account ID)",
    )
    integration_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="manual",
        comment="manual | whatsapp_cloud_api | instagram_messaging_api",
    )
    integration_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="disconnected",
        comment="connected | disconnected | error | pending",
    )
    encrypted_credentials: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Fernet-encrypted JSON payload for access tokens / webhook secrets",
    )
    automation_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    automation_mode: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="approval",
        comment="automatic | approval | disabled",
    )
    language_preferences: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "primary": "english",
            "allow_hinglish": True,
            "supported": ["english", "hindi", "hinglish"],
        },
    )
    context_window_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
        comment="Recent messages to include in memory context",
    )
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────
    personality: Mapped[Optional["PersonalityConfiguration"]] = relationship(
        "PersonalityConfiguration",
        back_populates="account",
        uselist=False,
        cascade="all, delete-orphan",
    )
    automation_rules: Mapped[list["AutomationRule"]] = relationship(
        "AutomationRule",
        back_populates="account",
        cascade="all, delete-orphan",
    )


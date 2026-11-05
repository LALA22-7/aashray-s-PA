"""
Personality configuration model for account-isolated AI communication styles.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.account import Account


class PersonalityConfiguration(Base, UUIDMixin, TimestampMixin):
    """
    Configures tone, language, verbosity, and behavioral parameters
    for AI replies originating from a specific account.
    """

    __tablename__ = "personality_configurations"

    account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    formality: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5,
        comment="0.0 (very casual) to 1.0 (strictly formal)",
    )
    friendliness: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.8,
        comment="0.0 (blunt/neutral) to 1.0 (warm/welcoming)",
    )
    humour: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.2,
        comment="0.0 (no jokes) to 1.0 (playful/witty)",
    )
    reply_length: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="short",
        comment="short | medium | long",
    )
    emoji_usage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.3,
        comment="0.0 (no emojis) to 1.0 (frequent emojis)",
    )
    language_preference: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="english",
        comment="english | hinglish | mixed",
    )
    hinglish_preference: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5,
        comment="0.0 (pure English) to 1.0 (heavy Hinglish)",
    )
    common_expressions: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="List of catchphrases or frequent greetings used by the persona",
    )
    professionalism: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5,
        comment="0.0 (laid-back peer) to 1.0 (corporate executive)",
    )
    sales_orientation: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="0.0 (non-commercial) to 1.0 (proactive lead converter)",
    )
    response_style: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="conversational",
        comment="conversational | direct | consultative",
    )
    system_prompt_override: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional developer or owner override for the AI system prompt",
    )

    # ── Relationship ──────────────────────────────────────────────
    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="personality",
    )

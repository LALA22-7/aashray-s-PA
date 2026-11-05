"""
Pydantic schemas for PersonalityConfiguration.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ReplyLength


class PersonalityConfigBase(BaseModel):
    """Common personality properties."""

    formality: float = Field(0.5, ge=0.0, le=1.0, description="0.0 casual to 1.0 formal")
    friendliness: float = Field(0.8, ge=0.0, le=1.0, description="0.0 neutral to 1.0 very friendly")
    humour: float = Field(0.2, ge=0.0, le=1.0, description="0.0 serious to 1.0 witty")
    reply_length: ReplyLength = Field(ReplyLength.SHORT, description="Response length")
    emoji_usage: float = Field(0.3, ge=0.0, le=1.0, description="0.0 none to 1.0 frequent")
    language_preference: str = Field("english", description="english | hinglish | mixed")
    hinglish_preference: float = Field(0.5, ge=0.0, le=1.0, description="0.0 pure english to 1.0 hinglish")
    common_expressions: list[str] = Field(default_factory=list, description="List of typical expressions")
    professionalism: float = Field(0.5, ge=0.0, le=1.0, description="0.0 peer to 1.0 corporate")
    sales_orientation: float = Field(0.0, ge=0.0, le=1.0, description="0.0 non-commercial to 1.0 sales-driven")
    response_style: str = Field("conversational", description="conversational | direct | consultative")
    system_prompt_override: Optional[str] = Field(None, description="Optional custom prompt instructions")


class PersonalityConfigCreate(PersonalityConfigBase):
    """Schema for initializing personality on account creation."""
    pass


class PersonalityConfigUpdate(BaseModel):
    """Schema for partial update of personality configuration."""

    formality: Optional[float] = Field(None, ge=0.0, le=1.0)
    friendliness: Optional[float] = Field(None, ge=0.0, le=1.0)
    humour: Optional[float] = Field(None, ge=0.0, le=1.0)
    reply_length: Optional[ReplyLength] = None
    emoji_usage: Optional[float] = Field(None, ge=0.0, le=1.0)
    language_preference: Optional[str] = None
    hinglish_preference: Optional[float] = Field(None, ge=0.0, le=1.0)
    common_expressions: Optional[list[str]] = None
    professionalism: Optional[float] = Field(None, ge=0.0, le=1.0)
    sales_orientation: Optional[float] = Field(None, ge=0.0, le=1.0)
    response_style: Optional[str] = None
    system_prompt_override: Optional[str] = None


class PersonalityConfigRead(PersonalityConfigBase):
    """Schema for reading personality configuration."""

    id: str
    account_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


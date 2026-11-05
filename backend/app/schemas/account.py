"""
Pydantic schemas for Account management.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    AccountType,
    AutomationMode,
    IntegrationStatus,
    IntegrationType,
    PlatformType,
)
from app.schemas.personality import PersonalityConfigCreate, PersonalityConfigRead


class AccountBase(BaseModel):
    """Common attributes for an Account."""

    platform: PlatformType = Field(..., description="whatsapp | instagram")
    account_type: AccountType = Field(..., description="personal | business")
    display_name: str = Field(..., min_length=1, max_length=128)
    phone_number: Optional[str] = Field(None, max_length=32, description="Associated phone number")
    platform_account_id: Optional[str] = Field(None, max_length=128)
    integration_type: IntegrationType = Field(IntegrationType.MANUAL)
    automation_enabled: bool = Field(False)
    automation_mode: AutomationMode = Field(AutomationMode.APPROVAL)
    language_preferences: dict[str, Any] = Field(
        default_factory=lambda: {
            "primary": "english",
            "allow_hinglish": True,
            "supported": ["english", "hindi", "hinglish"],
        }
    )
    context_window_size: int = Field(10, ge=1, le=50)


class AccountCreate(AccountBase):
    """Schema for creating a new Account."""

    personality: Optional[PersonalityConfigCreate] = None
    credentials: Optional[str] = Field(None, description="Raw credential/token string to be encrypted")


class AccountUpdate(BaseModel):
    """Schema for partial update of an Account."""

    display_name: Optional[str] = Field(None, min_length=1, max_length=128)
    phone_number: Optional[str] = Field(None, max_length=32)
    platform_account_id: Optional[str] = Field(None, max_length=128)
    integration_type: Optional[IntegrationType] = None
    automation_enabled: Optional[bool] = None
    automation_mode: Optional[AutomationMode] = None
    language_preferences: Optional[dict[str, Any]] = None
    context_window_size: Optional[int] = Field(None, ge=1, le=50)


class AccountConnectRequest(BaseModel):
    """Schema for connecting an account via credentials."""

    credentials: str = Field(..., min_length=1, description="Raw API token or credential payload")
    platform_account_id: Optional[str] = Field(None, description="External account identifier")


class AccountRead(AccountBase):
    """Public account information (never leaks raw credentials)."""

    id: str
    integration_status: IntegrationStatus
    has_credentials: bool = Field(..., description="Indicates whether credentials are stored")
    created_at: datetime
    updated_at: datetime
    last_sync_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AccountDetailRead(AccountRead):
    """Detailed account information including personality configuration."""

    personality: Optional[PersonalityConfigRead] = None


class AccountStatusSummary(BaseModel):
    """Status summary card for the control dashboard."""

    id: str
    display_name: str
    platform: PlatformType
    account_type: AccountType
    phone_number: Optional[str] = None
    integration_type: IntegrationType
    integration_status: IntegrationStatus
    automation_enabled: bool
    automation_mode: AutomationMode
    last_sync_at: Optional[datetime] = None

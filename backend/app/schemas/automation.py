"""
Pydantic schemas for automation rules and system-wide automation status.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class AutomationGlobalSettings(BaseModel):
    """Global and account-level automation settings overview."""

    global_paused: bool = Field(False, description="Whether all automations are temporarily halted")
    emergency_stopped: bool = Field(False, description="Emergency lock preventing any outbound generation")
    active_accounts_count: int
    automatic_mode_accounts_count: int
    approval_mode_accounts_count: int
    disabled_mode_accounts_count: int


class AutomationSettingsUpdate(BaseModel):
    """Update global automation controls."""

    action: str = Field(..., description="pause | resume | emergency-stop")
    reason: Optional[str] = Field(None, description="Audit reason for state change")


class AutomationRuleBase(BaseModel):
    """Base schema for automation rule."""

    rule_name: str = Field(..., min_length=1, max_length=128)
    rule_type: str = Field(..., description="auto_reply | require_approval | escalate | block")
    conditions: dict[str, Any] = Field(default_factory=dict)
    actions: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = Field(True)
    priority: int = Field(0)


class AutomationRuleCreate(AutomationRuleBase):
    """Creation schema for automation rule."""
    pass


class AutomationRuleRead(AutomationRuleBase):
    """Read schema for automation rule."""

    id: str
    account_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

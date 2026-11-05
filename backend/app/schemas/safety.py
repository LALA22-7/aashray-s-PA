"""
Pydantic schemas for Safety Policy, Audit Logging, and Lead Tracking.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class PolicyAction(str, Enum):
    """Resulting server decision from Policy Evaluation."""
    SEND_AUTOMATIC = "send_automatic"
    QUEUE_FOR_APPROVAL = "queue_for_approval"
    DO_NOT_SEND = "do_not_send"
    ESCALATE = "escalate"


class LeadStatus(str, Enum):
    """Lead lifecycle state."""
    NEW = "new"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    CONVERTED = "converted"
    LOST = "lost"


class PolicyEvaluationResult(BaseModel):
    """Server-side authorization decision for an outbound message."""

    action: PolicyAction
    is_authorized: bool = Field(..., description="True ONLY if message is authorized to be dispatched automatically")
    reason: str
    requires_human: bool
    account_id: str
    conversation_id: Optional[str] = None


class AuditLogRead(BaseModel):
    """Audit log entry."""

    id: str
    account_id: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: dict[str, Any]
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadBase(BaseModel):
    """Base lead fields."""

    customer_name: Optional[str] = None
    enquiry: Optional[str] = None
    campaign_requirements: dict[str, Any] = Field(default_factory=dict)
    estimated_quantity: Optional[int] = None
    location: Optional[str] = None
    status: LeadStatus = Field(LeadStatus.NEW)
    follow_up_notes: Optional[str] = None


class LeadCreate(LeadBase):
    """Lead creation payload."""

    account_id: str
    conversation_id: str
    contact_id: str


class LeadUpdate(BaseModel):
    """Lead update payload."""

    customer_name: Optional[str] = None
    enquiry: Optional[str] = None
    campaign_requirements: Optional[dict[str, Any]] = None
    estimated_quantity: Optional[int] = None
    location: Optional[str] = None
    status: Optional[LeadStatus] = None
    follow_up_notes: Optional[str] = None


class LeadRead(LeadBase):
    """Lead public representation."""

    id: str
    account_id: str
    conversation_id: str
    contact_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookEventRead(BaseModel):
    """Webhook event representation."""

    id: str
    account_id: Optional[str] = None
    platform: str
    event_type: str
    platform_event_id: str
    processing_status: str
    error_message: Optional[str] = None
    received_at: datetime
    processed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

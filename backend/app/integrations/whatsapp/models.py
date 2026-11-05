"""
Pydantic data models for parsing official WhatsApp Cloud API webhook events.
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class WhatsAppProfile(BaseModel):
    name: Optional[str] = None


class WhatsAppContact(BaseModel):
    profile: Optional[WhatsAppProfile] = None
    wa_id: str

    model_config = ConfigDict(extra="ignore")


class WhatsAppTextMessage(BaseModel):
    body: str


class WhatsAppIncomingMessage(BaseModel):
    id: str
    from_: str = Field(..., alias="from")
    timestamp: str
    type: str = "text"
    text: Optional[WhatsAppTextMessage] = None

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class WhatsAppStatusUpdate(BaseModel):
    id: str
    status: str  # sent | delivered | read | failed
    timestamp: str
    recipient_id: str
    errors: Optional[list[dict[str, Any]]] = None

    model_config = ConfigDict(extra="ignore")


class WhatsAppMetadata(BaseModel):
    display_phone_number: Optional[str] = None
    phone_number_id: str

    model_config = ConfigDict(extra="ignore")


class WhatsAppValue(BaseModel):
    messaging_product: str
    metadata: WhatsAppMetadata
    contacts: Optional[list[WhatsAppContact]] = None
    messages: Optional[list[WhatsAppIncomingMessage]] = None
    statuses: Optional[list[WhatsAppStatusUpdate]] = None

    model_config = ConfigDict(extra="ignore")


class WhatsAppChange(BaseModel):
    value: WhatsAppValue
    field: str

    model_config = ConfigDict(extra="ignore")


class WhatsAppEntry(BaseModel):
    id: str
    changes: list[WhatsAppChange]

    model_config = ConfigDict(extra="ignore")


class WhatsAppWebhookPayload(BaseModel):
    """Root payload structure received from Meta for WhatsApp Webhooks."""
    object: str
    entry: list[WhatsAppEntry]

    model_config = ConfigDict(extra="ignore")


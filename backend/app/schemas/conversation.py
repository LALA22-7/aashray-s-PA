"""
Pydantic schemas for Contacts, Conversations, and Messages.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.ai.schemas import AIResponsePayload


class ContactBase(BaseModel):
    """Base contact attributes."""

    platform_contact_id: str
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    contact_metadata: dict[str, Any] = Field(default_factory=dict)


class ContactRead(ContactBase):
    """Contact public representation."""

    id: str
    account_id: str
    first_seen_at: datetime
    last_seen_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageBase(BaseModel):
    """Base message attributes."""

    content: str = Field(..., min_length=1)
    message_type: str = Field("text")
    direction: str = Field("inbound", description="inbound | outbound")
    sender_type: str = Field("contact", description="contact | assistant | owner")


class MessageCreate(MessageBase):
    """Payload to record a new message."""

    platform_message_id: Optional[str] = None
    ai_metadata: Optional[dict[str, Any]] = None
    delivery_status: str = Field("received")
    is_ai_generated: bool = Field(False)
    owner_approved: bool = Field(True)


class MessageRead(MessageBase):
    """Message read model."""

    id: str
    conversation_id: str
    account_id: str
    platform_message_id: Optional[str] = None
    ai_metadata: Optional[dict[str, Any]] = None
    delivery_status: str
    is_ai_generated: bool
    owner_approved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationRead(BaseModel):
    """Conversation summary read model."""

    id: str
    account_id: str
    contact_id: str
    status: str
    summary: Optional[str] = None
    message_count: int
    last_message_at: datetime
    contact: Optional[ContactRead] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationDetailRead(ConversationRead):
    """Detailed conversation including recent message history."""

    messages: list[MessageRead] = Field(default_factory=list)


class ConversationReplyRequest(BaseModel):
    """Request to trigger AI reply generation on an existing conversation thread."""

    auto_save_outbound: bool = Field(
        False, description="Whether to immediately record the AI reply as an outbound message"
    )
    custom_instruction: Optional[str] = Field(
        None, description="One-off guidance for this specific reply"
    )


class ManualMessageRequest(BaseModel):
    """
    AI-Assisted manual workflow for Personal Accounts:
    Owner supplies/pastes an incoming message, AI generates a candidate reply,
    and returns it for review & manual copy.
    """

    account_id: str = Field(..., description="Target Personal WhatsApp or Instagram Account")
    sender_contact_id: str = Field(..., description="Sender's phone or handle")
    sender_name: Optional[str] = Field(None, description="Friend/contact name")
    message_content: str = Field(..., min_length=1, description="Pasted incoming message text")
    record_in_history: bool = Field(True, description="Whether to persist in conversation thread")


class ManualMessageResponse(BaseModel):
    """Response returned to owner to copy and paste to WhatsApp/Instagram."""

    conversation_id: str
    contact_id: str
    incoming_message: str
    suggested_reply: AIResponsePayload
    copyable_text: str

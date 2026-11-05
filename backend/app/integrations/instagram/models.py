"""
Pydantic models for incoming Meta Instagram Messaging API webhooks.
Ref: https://developers.facebook.com/docs/messenger-platform/instagram/webhooks
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class InstagramSender(BaseModel):
    id: str


class InstagramRecipient(BaseModel):
    id: str


class InstagramMessageContent(BaseModel):
    mid: str
    text: Optional[str] = None
    is_echo: Optional[bool] = False
    attachments: Optional[list[dict[str, Any]]] = None


class InstagramRead(BaseModel):
    mid: Optional[str] = None
    watermark: Optional[int] = None


class InstagramDelivery(BaseModel):
    mids: Optional[list[str]] = None
    watermark: Optional[int] = None


class InstagramMessagingEvent(BaseModel):
    sender: InstagramSender
    recipient: InstagramRecipient
    timestamp: Optional[int] = None
    message: Optional[InstagramMessageContent] = None
    read: Optional[InstagramRead] = None
    delivery: Optional[InstagramDelivery] = None


class InstagramEntry(BaseModel):
    id: str
    time: Optional[int] = None
    messaging: list[InstagramMessagingEvent] = Field(default_factory=list)


class InstagramWebhookPayload(BaseModel):
    object: str
    entry: list[InstagramEntry] = Field(default_factory=list)

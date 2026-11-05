"""
Pydantic schemas for Business Knowledge Base management.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeCategory(str, Enum):
    """Categorization for business knowledge items."""
    AGENCY_INFO = "agency_info"
    SERVICE = "service"
    ADVERTISING_FORMAT = "advertising_format"
    PACKAGE = "package"
    PRICING = "pricing"
    MOQ = "moq"
    LOCATION = "location"
    FAQ = "faq"
    BOOKING_PROCESS = "booking_process"
    PAYMENT_INFO = "payment_info"
    DELIVERY_TIMELINE = "delivery_timeline"
    CONTACT_INFO = "contact_info"
    GENERAL = "general"


class BusinessKnowledgeBase(BaseModel):
    """Common attributes for business knowledge items."""

    category: KnowledgeCategory = Field(..., description="Knowledge category")
    title: str = Field(..., min_length=2, max_length=256, description="Short descriptive heading")
    content: str = Field(..., min_length=5, description="Factual information used by AI")
    account_id: Optional[str] = Field(None, description="Account ID if scoped, or None for all business accounts")
    is_active: bool = Field(True, description="Whether this knowledge is currently active")
    priority: int = Field(0, description="Order of importance (higher first)")
    knowledge_metadata: dict[str, Any] = Field(default_factory=dict)


class BusinessKnowledgeCreate(BusinessKnowledgeBase):
    """Payload to create a new knowledge item."""
    pass


class BusinessKnowledgeUpdate(BaseModel):
    """Payload to update an existing knowledge item."""

    category: Optional[KnowledgeCategory] = None
    title: Optional[str] = Field(None, min_length=2, max_length=256)
    content: Optional[str] = Field(None, min_length=5)
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    knowledge_metadata: Optional[dict[str, Any]] = None


class BusinessKnowledgeRead(BusinessKnowledgeBase):
    """Representation of a business knowledge item."""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeSummaryResponse(BaseModel):
    """Overview of active knowledge items for dashboard rendering."""

    total_items: int
    active_items: int
    categories_present: list[str]
    compiled_preview: str

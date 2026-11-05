"""
Pydantic schemas and enums for AI Engine requests, responses, and structured outputs.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageIntent(str, Enum):
    """Supported intent categories."""
    GREETING = "greeting"
    CASUAL_CONVERSATION = "casual_conversation"
    PERSONAL_QUESTION = "personal_question"
    GENERAL_QUESTION = "general_question"
    BUSINESS_ENQUIRY = "business_enquiry"
    PRICING_ENQUIRY = "pricing_enquiry"
    SERVICE_ENQUIRY = "service_enquiry"
    LEAD_GENERATION = "lead_generation"
    CUSTOMER_SUPPORT = "customer_support"
    COMPLAINT = "complaint"
    NEGOTIATION = "negotiation"
    FOLLOW_UP = "follow_up"
    SENSITIVE_CONVERSATION = "sensitive_conversation"
    UNKNOWN = "unknown"


class ConversationMode(str, Enum):
    """Communication mode based on account context."""
    PERSONAL = "personal"
    BUSINESS = "business"


class IntentClassificationResult(BaseModel):
    """Structured result from IntentClassifier."""

    intent: MessageIntent = Field(..., description="Classified intent")
    mode: ConversationMode = Field(..., description="personal or business mode")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    requires_human: bool = Field(False, description="True if intent requires human intervention")
    reason: Optional[str] = Field(None, description="Reason for escalation or classification")

    model_config = ConfigDict(extra="ignore")


class AIResponsePayload(BaseModel):
    """Unified structured response output from AI Engine."""

    intent: MessageIntent = Field(..., description="Identified intent")
    mode: ConversationMode = Field(..., description="Operating mode")
    reply: str = Field(..., min_length=1, description="Generated response text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score")
    requires_human: bool = Field(False, description="Whether human review is required")
    reason: Optional[str] = Field(None, description="Explanation when human is required")
    extracted_lead_info: Optional[dict[str, Any]] = Field(
        None, description="Extracted lead data like bottle count, location, target audience"
    )

    model_config = ConfigDict(extra="ignore")


class MessageHistoryItem(BaseModel):
    """Single item in conversation context history."""

    role: str = Field(..., description="user | assistant | contact")
    content: str = Field(..., min_length=1)


class GenerateReplyRequest(BaseModel):
    """Payload to trigger AI response generation."""

    account_id: str = Field(..., description="ID of the receiving Account")
    message: str = Field(..., min_length=1, description="Incoming message text")
    sender_name: Optional[str] = Field(None, description="Contact name or handle")
    conversation_history: list[MessageHistoryItem] = Field(
        default_factory=list, description="Prior conversation messages"
    )
    business_context: Optional[str] = Field(
        None, description="Verified business knowledge context if available"
    )


class TestMessageRequest(BaseModel):
    """Interactive preview/testing request from dashboard."""

    account_id: str = Field(..., description="Target account ID")
    message: str = Field(..., min_length=1, description="Simulated incoming message")
    sender_name: Optional[str] = Field("Alex", description="Simulated sender")
    conversation_history: list[MessageHistoryItem] = Field(default_factory=list)


class TestMessageResponse(BaseModel):
    """Result of test message generation."""

    account_id: str
    account_name: str
    platform: str
    account_type: str
    result: AIResponsePayload
    system_prompt_used: Optional[str] = None


class AISettingsRead(BaseModel):
    """Current AI provider and model configuration."""

    provider: str
    model: str
    has_api_key: bool
    temperature: float = 0.7
    available_providers: list[str] = ["gemini", "mock"]


class AISettingsUpdate(BaseModel):
    """Update AI engine runtime settings."""

    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)


"""
Deterministic Mock AI Provider for testing and offline development.
"""

import json
from typing import Optional, Type, TypeVar

from pydantic import BaseModel

from app.ai.providers.base import BaseAIProvider
from app.ai.schemas import (
    AIResponsePayload,
    ConversationMode,
    IntentClassificationResult,
    MessageIntent,
)

T = TypeVar("T", bound=BaseModel)


class MockAIProvider(BaseAIProvider):
    """
    Mock LLM provider returning realistic structured responses
    without making external API requests.
    """

    def __init__(self, is_available: bool = True) -> None:
        self.is_available = is_available

    def is_healthy(self) -> bool:
        return self.is_available

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        return "Hey! This is a mock response from Aashray'sPA."

    def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_model: Type[T],
        temperature: float = 0.7,
    ) -> T:
        prompt_lower = prompt.lower()
        sys_lower = system_instruction.lower()
        is_business = "business" in sys_lower or "agency" in sys_lower or "bottle" in prompt_lower

        # ── 1. If requesting IntentClassificationResult ──────────────
        if response_model == IntentClassificationResult:
            intent = self._classify_mock_intent(prompt_lower, is_business)
            mode = ConversationMode.BUSINESS if is_business else ConversationMode.PERSONAL
            requires_human = intent in (
                MessageIntent.COMPLAINT,
                MessageIntent.NEGOTIATION,
                MessageIntent.SENSITIVE_CONVERSATION,
            )
            return IntentClassificationResult(
                intent=intent,
                mode=mode,
                confidence=0.95,
                requires_human=requires_human,
                reason="Escalated due to sensitivity" if requires_human else None,
            )  # type: ignore

        # ── 2. If requesting AIResponsePayload ───────────────────────
        if response_model == AIResponsePayload:
            intent = self._classify_mock_intent(prompt_lower, is_business)
            mode = ConversationMode.BUSINESS if is_business else ConversationMode.PERSONAL
            requires_human = intent in (
                MessageIntent.COMPLAINT,
                MessageIntent.NEGOTIATION,
                MessageIntent.SENSITIVE_CONVERSATION,
            )

            reply = self._build_mock_reply(prompt_lower, intent, is_business, sys_lower)

            lead_info = None
            if intent in (MessageIntent.BUSINESS_ENQUIRY, MessageIntent.LEAD_GENERATION):
                lead_info = {"service": "bottle_advertising", "status": "preliminary"}

            return AIResponsePayload(
                intent=intent,
                mode=mode,
                reply=reply,
                confidence=0.92,
                requires_human=requires_human,
                reason="Human intervention required for negotiation/complaint" if requires_human else None,
                extracted_lead_info=lead_info,
            )  # type: ignore

        # Fallback for arbitrary model with default empty instance
        try:
            return response_model.model_validate({})
        except Exception:
            # Construct empty dummy JSON
            return response_model.model_validate(json.loads("{}"))

    def _classify_mock_intent(self, text: str, is_business: bool) -> MessageIntent:
        """Heuristic mock intent classification for testing."""
        # Check high-priority escalation and sensitive intents first
        if any(w in text for w in ["emergency", "hospital", "police", "legal", "court"]):
            return MessageIntent.SENSITIVE_CONVERSATION
        if any(w in text for w in ["complaint", "worst", "bad", "angry", "broken", "fraud", "damaged"]):
            return MessageIntent.COMPLAINT
        if any(w in text for w in ["discount", "deal", "lower price", "negotiate", "offer"]):
            return MessageIntent.NEGOTIATION
        if any(w in text for w in ["price", "cost", "charge", "rate", "how much"]):
            return MessageIntent.PRICING_ENQUIRY if is_business else MessageIntent.GENERAL_QUESTION
        if any(w in text for w in ["bottle", "campaign", "ad", "advertising", "service"]):
            return MessageIntent.BUSINESS_ENQUIRY
        if any(w in text for w in ["hi", "hello", "hey", "namaste", "sup", "good morning"]):
            return MessageIntent.GREETING
        if any(w in text for w in ["where are you", "kya kar raha", "what are you doing"]):
            return MessageIntent.PERSONAL_QUESTION

        return MessageIntent.CASUAL_CONVERSATION if not is_business else MessageIntent.BUSINESS_ENQUIRY

    def _build_mock_reply(
        self, prompt_lower: str, intent: MessageIntent, is_business: bool, sys_lower: str
    ) -> str:
        """Generate representative mock replies according to persona."""
        use_hinglish = "hinglish" in sys_lower

        if not is_business:
            # Personal Persona
            if intent == MessageIntent.GREETING:
                return "Hey! Kya haal chaal?" if use_hinglish else "Hey! Good to hear from you. How are things?"
            if intent == MessageIntent.PERSONAL_QUESTION:
                return "Bas chal raha hai sab chill. What about you?" if use_hinglish else "All good here! Just catching up on things. How about you?"
            if intent == MessageIntent.SENSITIVE_CONVERSATION:
                return "Hey, let's talk about this directly over a call when free."
            return "Haan bilkul, sounds good!" if use_hinglish else "Sounds good, let me know!"

        # Business Persona (Bottle Advertising Agency)
        if intent in (MessageIntent.BUSINESS_ENQUIRY, MessageIntent.PRICING_ENQUIRY):
            return (
                "Hey! Yes, we provide bottle advertising campaigns. Pricing depends on "
                "the campaign requirements, quantity, and target location. Could you tell me "
                "approximately how many bottles you're considering and which location you're targeting?"
            )
        if intent == MessageIntent.GREETING:
            return "Hi there! Welcome to Aashray's Bottle Advertising Agency. How can we assist your brand today?"
        if intent == MessageIntent.COMPLAINT:
            return "I sincerely apologize for the inconvenience. I'm escalating this immediately to our management team to resolve it right away."
        if intent == MessageIntent.NEGOTIATION:
            return "Thank you for your interest! For custom volume discounts and tailored packages, our agency lead will connect with you directly."

        return "Thank you for reaching out to us. Could you share more details about your brand campaign?"

"""
Central AI Orchestration Engine for Aashray'sPA.
"""

import logging
from typing import Optional

from app.ai.intent_classifier import IntentClassifier
from app.ai.personality import PersonalityEngine
from app.ai.providers import get_ai_provider
from app.ai.providers.base import BaseAIProvider
from app.ai.schemas import (
    AIResponsePayload,
    ConversationMode,
    GenerateReplyRequest,
    MessageIntent,
)
from app.models.account import Account
from app.models.enums import AccountType

logger = logging.getLogger("aashrayspa.ai.engine")


class AIEngine:
    """
    Coordinates intent classification, dynamic persona assembly,
    prompt generation, structured LLM execution, and safety checks.
    """

    def __init__(self, provider: Optional[BaseAIProvider] = None) -> None:
        self.provider = provider or get_ai_provider()
        self.intent_classifier = IntentClassifier(self.provider)

    def process_message(
        self,
        account: Account,
        request: GenerateReplyRequest,
    ) -> AIResponsePayload:
        """
        End-to-end execution pipeline for an incoming message.
        """
        is_business = account.account_type == AccountType.BUSINESS.value

        # Format history string
        history_lines = []
        for item in request.conversation_history[-account.context_window_size :]:
            history_lines.append(f"{item.role.capitalize()}: {item.content}")
        history_text = "\n".join(history_lines) if history_lines else None

        # ── 1. Build System Instruction with Account's Persona ────────
        system_instruction = PersonalityEngine.build_system_instruction(
            account=account,
            personality=account.personality,
            business_knowledge_summary=request.business_context,
        )

        # ── 2. Format User Input Prompt (Prompt-Injection Safe) ───────
        prompt = PersonalityEngine.wrap_user_message(
            message=request.message,
            sender_name=request.sender_name,
            conversation_history_text=history_text,
        )

        # ── 3. Generate Structured Response ───────────────────────────
        try:
            response = self.provider.generate_structured(
                prompt=prompt,
                system_instruction=system_instruction,
                response_model=AIResponsePayload,
                temperature=0.6,
            )
        except Exception as exc:
            logger.error("AI Provider generation failed; constructing safe escalation response", exc_info=exc)
            # Safe fallback response
            return AIResponsePayload(
                intent=MessageIntent.UNKNOWN,
                mode=ConversationMode.BUSINESS if is_business else ConversationMode.PERSONAL,
                reply=(
                    "Thank you for your message. Let me review this and get back to you shortly."
                    if is_business
                    else "Hey, got your message! Will catch up in a bit."
                ),
                confidence=0.5,
                requires_human=True,
                reason=f"LLM execution error: {str(exc)}",
            )

        # ── 4. Enforce Backend Safety Policy ─────────────────────────
        # Backend always has ultimate authority over human escalation
        response.mode = (
            ConversationMode.BUSINESS if is_business else ConversationMode.PERSONAL
        )

        if response.confidence < 0.65:
            response.requires_human = True
            if not response.reason:
                response.reason = f"Low confidence ({response.confidence:.2f})"

        if response.intent in (
            MessageIntent.COMPLAINT,
            MessageIntent.NEGOTIATION,
            MessageIntent.SENSITIVE_CONVERSATION,
        ):
            response.requires_human = True
            if not response.reason:
                response.reason = f"Sensitive intent detected: {response.intent.value}"

        return response

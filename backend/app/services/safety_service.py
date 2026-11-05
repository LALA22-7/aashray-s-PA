"""
Safety & Policy Response Engine.
Enforces multi-layer server-side authorization before any outbound message delivery.
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.ai.schemas import AIResponsePayload, MessageIntent
from app.models.account import Account
from app.models.enums import AutomationMode
from app.models.lead import Lead
from app.repositories.account_repo import AccountRepository
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.safety_repo import (
    AuditLogRepository,
    LeadRepository,
    WebhookEventRepository,
)
from app.schemas.safety import LeadStatus, PolicyAction, PolicyEvaluationResult
from app.services.account_service import AccountService

logger = logging.getLogger("aashrayspa.safety")

MINIMUM_AUTOMATIC_CONFIDENCE_THRESHOLD = 0.70


class SafetyService:
    """
    Enforces independent server-side safety checks, rate limiting,
    lead capture, and idempotent duplicate prevention.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit_repo = AuditLogRepository(db)
        self.webhook_repo = WebhookEventRepository(db)
        self.lead_repo = LeadRepository(db)
        self.account_repo = AccountRepository(db)
        self.conv_repo = ConversationRepository(db)

    # ── Policy Evaluation Engine ───────────────────────────────────

    def evaluate_outbound_policy(
        self,
        account: Account,
        ai_response: AIResponsePayload,
        conversation_id: Optional[str] = None,
    ) -> PolicyEvaluationResult:
        """
        Determines whether an AI-generated reply is authorized to be dispatched automatically,
        queued for human approval, or completely suppressed.
        """
        global_status = AccountService.get_global_automation_status()

        # 1. Global Emergency Stop check
        if global_status.get("emergency_stopped"):
            self.audit_repo.log(
                action="outbound_blocked_emergency_stop",
                account_id=account.id,
                resource_type="conversation",
                resource_id=conversation_id,
                details={"reason": "Emergency Stop is active across the system"},
            )
            return PolicyEvaluationResult(
                action=PolicyAction.DO_NOT_SEND,
                is_authorized=False,
                reason="Global Emergency Stop is active. All outbound generation is locked.",
                requires_human=True,
                account_id=account.id,
                conversation_id=conversation_id,
            )

        # 2. Global Automation Pause check
        if global_status.get("global_paused"):
            self.audit_repo.log(
                action="outbound_queued_global_pause",
                account_id=account.id,
                resource_type="conversation",
                resource_id=conversation_id,
                details={"reason": "Global automations are paused"},
            )
            return PolicyEvaluationResult(
                action=PolicyAction.QUEUE_FOR_APPROVAL,
                is_authorized=False,
                reason="Automations are globally paused. Reply queued for manual review.",
                requires_human=True,
                account_id=account.id,
                conversation_id=conversation_id,
            )

        # 3. Account-level automation toggle
        if not account.automation_enabled:
            return PolicyEvaluationResult(
                action=PolicyAction.QUEUE_FOR_APPROVAL,
                is_authorized=False,
                reason=f"Automation is disabled on account '{account.display_name}'.",
                requires_human=True,
                account_id=account.id,
                conversation_id=conversation_id,
            )

        # 4. Account Automation Mode: DISABLED
        if account.automation_mode == AutomationMode.DISABLED.value:
            return PolicyEvaluationResult(
                action=PolicyAction.DO_NOT_SEND,
                is_authorized=False,
                reason="Account automation mode is set to DISABLED.",
                requires_human=False,
                account_id=account.id,
                conversation_id=conversation_id,
            )

        # 5. Account Automation Mode: APPROVAL
        if account.automation_mode == AutomationMode.APPROVAL.value:
            self.audit_repo.log(
                action="outbound_queued_approval_mode",
                account_id=account.id,
                resource_type="conversation",
                resource_id=conversation_id,
                details={"intent": ai_response.intent.value, "confidence": ai_response.confidence},
            )
            return PolicyEvaluationResult(
                action=PolicyAction.QUEUE_FOR_APPROVAL,
                is_authorized=False,
                reason="Account requires owner review and approval before dispatching replies.",
                requires_human=True,
                account_id=account.id,
                conversation_id=conversation_id,
            )

        # 6. Account Automation Mode: AUTOMATIC -> Verify safety criteria
        if account.automation_mode == AutomationMode.AUTOMATIC.value:
            # Check A: Explicit human requirement flagged by intent / safety rules
            if ai_response.requires_human:
                self.audit_repo.log(
                    action="outbound_escalated_sensitive_intent",
                    account_id=account.id,
                    resource_type="conversation",
                    resource_id=conversation_id,
                    details={
                        "intent": ai_response.intent.value,
                        "reason": ai_response.reason,
                    },
                )
                return PolicyEvaluationResult(
                    action=PolicyAction.ESCALATE,
                    is_authorized=False,
                    reason=ai_response.reason or f"Sensitive intent '{ai_response.intent.value}' escalated.",
                    requires_human=True,
                    account_id=account.id,
                    conversation_id=conversation_id,
                )

            # Check B: Minimum confidence threshold
            if ai_response.confidence < MINIMUM_AUTOMATIC_CONFIDENCE_THRESHOLD:
                self.audit_repo.log(
                    action="outbound_escalated_low_confidence",
                    account_id=account.id,
                    resource_type="conversation",
                    resource_id=conversation_id,
                    details={
                        "confidence": ai_response.confidence,
                        "threshold": MINIMUM_AUTOMATIC_CONFIDENCE_THRESHOLD,
                    },
                )
                return PolicyEvaluationResult(
                    action=PolicyAction.QUEUE_FOR_APPROVAL,
                    is_authorized=False,
                    reason=f"AI confidence ({ai_response.confidence:.2f}) is below automatic threshold ({MINIMUM_AUTOMATIC_CONFIDENCE_THRESHOLD:.2f}).",
                    requires_human=True,
                    account_id=account.id,
                    conversation_id=conversation_id,
                )

            # All automated policy criteria satisfied
            self.audit_repo.log(
                action="outbound_authorized_automatic",
                account_id=account.id,
                resource_type="conversation",
                resource_id=conversation_id,
                details={
                    "intent": ai_response.intent.value,
                    "confidence": ai_response.confidence,
                },
            )
            return PolicyEvaluationResult(
                action=PolicyAction.SEND_AUTOMATIC,
                is_authorized=True,
                reason="Authorized for immediate automatic outbound dispatch.",
                requires_human=False,
                account_id=account.id,
                conversation_id=conversation_id,
            )

        # Fallback safe default
        return PolicyEvaluationResult(
            action=PolicyAction.QUEUE_FOR_APPROVAL,
            is_authorized=False,
            reason="Unrecognized policy state; queued for safety.",
            requires_human=True,
            account_id=account.id,
            conversation_id=conversation_id,
        )

    # ── Automated Lead Capture ─────────────────────────────────────

    def capture_lead_if_qualified(
        self,
        account: Account,
        conversation_id: str,
        contact_id: str,
        ai_response: AIResponsePayload,
        customer_name: Optional[str] = None,
        incoming_message: Optional[str] = None,
    ) -> Optional[Lead]:
        """
        Extracts and records qualified advertising leads from incoming business chats.
        """
        lead_intents = (
            MessageIntent.BUSINESS_ENQUIRY,
            MessageIntent.LEAD_GENERATION,
            MessageIntent.PRICING_ENQUIRY,
            MessageIntent.SERVICE_ENQUIRY,
        )

        if ai_response.intent not in lead_intents:
            return None

        # Check existing lead for this conversation
        lead = self.lead_repo.get_by_conversation_id(conversation_id)
        extracted = ai_response.extracted_lead_info or {}

        qty = extracted.get("quantity") or extracted.get("estimated_quantity")
        location = extracted.get("location") or extracted.get("city")

        if not lead:
            lead = Lead(
                account_id=account.id,
                conversation_id=conversation_id,
                contact_id=contact_id,
                customer_name=customer_name or "New Prospect",
                enquiry=incoming_message or "Bottle Advertising Enquiry",
                campaign_requirements=extracted,
                estimated_quantity=qty if isinstance(qty, int) else None,
                location=location if isinstance(location, str) else None,
                status=LeadStatus.QUALIFIED.value if qty else LeadStatus.NEW.value,
            )
            saved = self.lead_repo.create(lead)
            self.audit_repo.log(
                action="lead_captured",
                account_id=account.id,
                resource_type="lead",
                resource_id=saved.id,
                details={"customer": customer_name, "intent": ai_response.intent.value},
            )
            return saved
        else:
            # Update existing lead with newly captured data
            if qty and not lead.estimated_quantity:
                lead.estimated_quantity = qty
                lead.status = LeadStatus.QUALIFIED.value
            if location and not lead.location:
                lead.location = location
            if extracted:
                lead.campaign_requirements.update(extracted)
            return self.lead_repo.update(lead)

    # ── Idempotent Webhook Deduplication ───────────────────────────

    def is_duplicate_webhook(self, platform_event_id: str) -> bool:
        """
        Check if an external event ID has already been recorded.
        Prevents processing duplicate webhook retries from Meta.
        """
        existing = self.webhook_repo.get_by_platform_event_id(platform_event_id)
        return existing is not None


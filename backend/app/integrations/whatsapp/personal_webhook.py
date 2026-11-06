"""
Orchestrates incoming messages from Ashray's Personal WhatsApp Companion Bridge,
two-way synchronization, AI generation, and outbound dispatch.
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.ai.engine import AIEngine
from app.ai.schemas import GenerateReplyRequest
from app.integrations.whatsapp.personal_adapter import PersonalWhatsAppAdapter
from app.models.enums import AccountType, PlatformType
from app.repositories.account_repo import AccountRepository
from app.schemas.conversation import MessageCreate
from app.schemas.safety import PolicyAction
from app.services.conversation_service import ConversationService
from app.services.safety_service import SafetyService

logger = logging.getLogger("aashrayspa.integrations.whatsapp_personal.webhook")


def process_personal_whatsapp_webhook(
    payload: dict[str, Any],
    db: Session,
    adapter: PersonalWhatsAppAdapter,
) -> dict[str, Any]:
    """
    Processes incoming message events forwarded by the Baileys companion bridge.
    """
    account_repo = AccountRepository(db)
    conv_service = ConversationService(db)
    safety_service = SafetyService(db)
    ai_engine = AIEngine()

    # 1. Resolve Personal WhatsApp Account
    wa_accounts = account_repo.get_all(
        platform=PlatformType.WHATSAPP.value,
        account_type=AccountType.PERSONAL.value,
    )
    account = wa_accounts[0] if wa_accounts else None

    if not account:
        logger.error("No configured Personal WhatsApp account found.")
        return {"status": "ignored", "reason": "no_account_found"}

    platform_msg_id = payload.get("platform_message_id") or f"wa_personal_{payload.get('timestamp')}"
    sender_phone = payload.get("from", "")
    sender_name = payload.get("sender_name") or sender_phone
    message_text = payload.get("text", "")
    is_from_me = payload.get("is_from_me", False)

    if not message_text or not sender_phone:
        return {"status": "skipped", "reason": "empty_content_or_sender"}

    # 2. Resolve Contact and Conversation
    contact = conv_service.get_or_create_contact(
        account_id=account.id,
        platform_contact_id=sender_phone,
        display_name=sender_name,
        phone_number=sender_phone,
    )
    conv = conv_service.get_or_create_conversation(
        account_id=account.id,
        contact_id=contact.id,
    )

    # 3. Two-Way Sync: If owner sent from physical phone, record outbound
    if is_from_me:
        logger.info(f"Syncing owner outbound message sent from physical phone to {sender_phone}")
        conv_service.record_message(
            conversation_id=conv.id,
            data=MessageCreate(
                platform_message_id=platform_msg_id,
                direction="outbound",
                content=message_text,
                sender_type="owner",
                delivery_status="sent",
                is_ai_generated=False,
                owner_approved=True,
            ),
        )
        return {"status": "synced", "direction": "outbound"}

    # 4. Inbound Message Handling
    # Idempotency check: Ignore duplicate deliveries
    if safety_service.is_duplicate_webhook(platform_msg_id):
        logger.info(f"Duplicate personal WhatsApp message '{platform_msg_id}' ignored.")
        return {"status": "duplicate_ignored"}

    # Record event in audit log
    event_record = safety_service.webhook_repo.record_event(
        platform="whatsapp_personal",
        event_type="message",
        platform_event_id=platform_msg_id,
        raw_payload=payload,
        account_id=account.id,
    )

    # Record incoming message in DB
    conv_service.record_message(
        conversation_id=conv.id,
        data=MessageCreate(
            platform_message_id=platform_msg_id,
            direction="inbound",
            content=message_text,
            sender_type="contact",
            delivery_status="received",
        ),
    )

    # 5. Sliding-Window History Context
    history = conv_service.get_conversation_context(
        conv.id, limit=account.context_window_size
    )

    # 6. AI Engine Response Generation (Personal Persona)
    gen_req = GenerateReplyRequest(
        account_id=account.id,
        message=message_text,
        sender_name=sender_name,
        conversation_history=history[:-1] if history else [],
        business_context=None,  # Strict isolation: no business knowledge in personal chats
    )
    ai_reply = ai_engine.process_message(account=account, request=gen_req)

    # 7. Safety Policy Evaluation
    policy_decision = safety_service.evaluate_outbound_policy(
        account=account,
        ai_response=ai_reply,
        conversation_id=conv.id,
    )

    # 8. Outbound Dispatch Action
    if policy_decision.action == PolicyAction.SEND_AUTOMATIC:
        dispatch_res = adapter.send_text_message(
            recipient_id=sender_phone,
            text=ai_reply.reply,
            account_id=account.id,
        )

        sent_id = None
        if dispatch_res.get("success"):
            data = dispatch_res.get("data", {})
            sent_id = data.get("message_id")

        conv_service.record_message(
            conversation_id=conv.id,
            data=MessageCreate(
                platform_message_id=sent_id,
                direction="outbound",
                content=ai_reply.reply,
                sender_type="assistant",
                delivery_status="sent" if dispatch_res.get("success") else "failed",
                is_ai_generated=True,
                owner_approved=True,
                ai_metadata=ai_reply.model_dump(),
            ),
        )
    elif policy_decision.action in (
        PolicyAction.QUEUE_FOR_APPROVAL,
        PolicyAction.ESCALATE,
    ):
        # Hold in Approval Centre for Ashray to review
        conv_service.record_message(
            conversation_id=conv.id,
            data=MessageCreate(
                direction="outbound",
                content=ai_reply.reply,
                sender_type="assistant",
                delivery_status="pending",
                is_ai_generated=True,
                owner_approved=False,
                ai_metadata={
                    **ai_reply.model_dump(),
                    "policy_action": policy_decision.action.value,
                    "policy_reason": policy_decision.reason,
                },
            ),
        )

    safety_service.webhook_repo.mark_processed(event_record, status="processed")

    return {
        "status": "success",
        "action": policy_decision.action.value,
        "reply": ai_reply.reply,
    }

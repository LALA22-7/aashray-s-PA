"""
Orchestrates incoming WhatsApp webhook processing, delivery receipts,
AI generation, safety policy enforcement, and automatic outbound dispatch.
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.ai.engine import AIEngine
from app.ai.schemas import GenerateReplyRequest
from app.integrations.whatsapp.adapter import WhatsAppAdapter
from app.integrations.whatsapp.models import WhatsAppWebhookPayload
from app.models.enums import AccountType, PlatformType
from app.repositories.account_repo import AccountRepository
from app.schemas.conversation import MessageCreate
from app.schemas.safety import PolicyAction
from app.services.conversation_service import ConversationService
from app.services.knowledge_service import KnowledgeService
from app.services.safety_service import SafetyService

logger = logging.getLogger("aashrayspa.integrations.whatsapp.webhook")


def process_whatsapp_webhook(
    payload_dict: dict[str, Any],
    db: Session,
    adapter: WhatsAppAdapter,
) -> dict[str, Any]:
    """
    Main entry point for processing verified WhatsApp Cloud API webhook events.
    """
    try:
        payload = WhatsAppWebhookPayload.model_validate(payload_dict)
    except Exception as exc:
        logger.error(f"Invalid WhatsApp webhook payload schema: {exc}")
        return {"status": "ignored", "reason": "invalid_schema"}

    account_repo = AccountRepository(db)
    conv_service = ConversationService(db)
    safety_service = SafetyService(db)
    knowledge_service = KnowledgeService(db)
    ai_engine = AIEngine()

    processed_messages_count = 0
    status_updates_count = 0

    for entry in payload.entry:
        for change in entry.changes:
            val = change.value
            phone_num_id = val.metadata.phone_number_id

            # ── 1. Strict Account Identification ──────────────────────
            # Lookup Account by platform_account_id or default to Business WhatsApp
            account = account_repo.get_by_platform_account_id(phone_num_id)
            if not account:
                # Fallback to seeded Business WhatsApp account
                wa_accounts = account_repo.get_all(
                    platform=PlatformType.WHATSAPP.value,
                    account_type=AccountType.BUSINESS.value,
                )
                account = wa_accounts[0] if wa_accounts else None

            if not account:
                logger.error(f"No configured WhatsApp business account matches phone_id '{phone_num_id}'")
                continue

            # ── 2. Handle Status Receipts (delivered, read, failed) ────
            if val.statuses:
                for status_item in val.statuses:
                    msg = conv_service.repo.get_message_by_platform_id(status_item.id)
                    if msg:
                        msg.delivery_status = status_item.status
                        db.commit()
                        status_updates_count += 1
                        logger.info(
                            f"Updated message '{status_item.id}' delivery_status to '{status_item.status}'"
                        )

            # ── 3. Handle Inbound Messages ────────────────────────────
            if val.messages:
                # Build contact name map
                contact_names = {}
                if val.contacts:
                    for c in val.contacts:
                        contact_names[c.wa_id] = c.profile.name if c.profile else c.wa_id

                for in_msg in val.messages:
                    # Idempotency check: Ignore duplicate retries
                    if safety_service.is_duplicate_webhook(in_msg.id):
                        logger.info(f"Duplicate WhatsApp webhook event '{in_msg.id}' ignored.")
                        continue

                    # Record incoming raw webhook event
                    event_record = safety_service.webhook_repo.record_event(
                        platform="whatsapp",
                        event_type="message",
                        platform_event_id=in_msg.id,
                        raw_payload=payload_dict,
                        account_id=account.id,
                    )

                    sender_phone = in_msg.from_
                    sender_name = contact_names.get(sender_phone, sender_phone)
                    message_text = in_msg.text.body if in_msg.text else ""

                    if not message_text:
                        safety_service.webhook_repo.mark_processed(
                            event_record, status="skipped", error="Non-text message"
                        )
                        continue

                    # ── A. Resolve Contact & Conversation ─────────────
                    contact = conv_service.get_or_create_contact(
                        account_id=account.id,
                        platform_contact_id=sender_phone,
                        display_name=sender_name,
                        phone_number=sender_phone,
                    )
                    conv = conv_service.get_or_create_conversation(
                        account_id=account.id, contact_id=contact.id
                    )

                    # ── B. Record Inbound Message ─────────────────────
                    conv_service.record_message(
                        conversation_id=conv.id,
                        data=MessageCreate(
                            platform_message_id=in_msg.id,
                            direction="inbound",
                            content=message_text,
                            sender_type="contact",
                            delivery_status="received",
                        ),
                    )

                    # ── C. Sliding Window History Context ─────────────
                    history = conv_service.get_conversation_context(
                        conv.id, limit=account.context_window_size
                    )

                    # ── D. Verified Business Knowledge ───────────────
                    biz_context = knowledge_service.compile_knowledge_for_account(account.id)

                    # ── E. AI Engine Response Generation ──────────────
                    gen_req = GenerateReplyRequest(
                        account_id=account.id,
                        message=message_text,
                        sender_name=sender_name,
                        conversation_history=history[:-1] if history else [],
                        business_context=biz_context,
                    )
                    ai_reply = ai_engine.process_message(account=account, request=gen_req)

                    # ── F. Server-Side Safety Policy Evaluation ───────
                    policy_decision = safety_service.evaluate_outbound_policy(
                        account=account,
                        ai_response=ai_reply,
                        conversation_id=conv.id,
                    )

                    # ── G. Outbound Dispatch Action ───────────────────
                    if policy_decision.action == PolicyAction.SEND_AUTOMATIC:
                        dispatch_res = adapter.send_text_message(
                            recipient_id=sender_phone,
                            text=ai_reply.reply,
                            account_id=account.id,
                        )

                        wamid = None
                        if dispatch_res.get("success"):
                            data = dispatch_res.get("data", {})
                            messages_res = data.get("messages", [])
                            if messages_res:
                                wamid = messages_res[0].get("id")

                        # Record dispatched outbound message
                        conv_service.record_message(
                            conversation_id=conv.id,
                            data=MessageCreate(
                                platform_message_id=wamid,
                                direction="outbound",
                                content=ai_reply.reply,
                                sender_type="assistant",
                                delivery_status="sent" if dispatch_res.get("success") else "failed",
                                is_ai_generated=True,
                                owner_approved=True,
                                ai_metadata=ai_reply.model_dump(),
                            ),
                        )

                        # Qualify and capture advertising lead
                        safety_service.capture_lead_if_qualified(
                            account=account,
                            conversation_id=conv.id,
                            contact_id=contact.id,
                            ai_response=ai_reply,
                            customer_name=sender_name,
                            incoming_message=message_text,
                        )

                    elif policy_decision.action in (
                        PolicyAction.QUEUE_FOR_APPROVAL,
                        PolicyAction.ESCALATE,
                    ):
                        # Persist draft for owner review
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

                    # Mark webhook processed
                    safety_service.webhook_repo.mark_processed(event_record, status="processed")
                    processed_messages_count += 1

    return {
        "status": "success",
        "processed_messages": processed_messages_count,
        "status_updates": status_updates_count,
    }

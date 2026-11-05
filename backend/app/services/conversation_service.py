"""
Service for conversation management, sliding-window memory retrieval,
and AI-assisted manual workflows for personal accounts.
"""

from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.ai.engine import AIEngine
from app.ai.schemas import (
    AIResponsePayload,
    GenerateReplyRequest,
    MessageHistoryItem,
)
from app.core.exceptions import NotFoundException
from app.models.contact import Contact
from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.account_repo import AccountRepository
from app.repositories.conversation_repo import ConversationRepository
from app.schemas.conversation import (
    ManualMessageRequest,
    ManualMessageResponse,
    MessageCreate,
)
from app.services.knowledge_service import KnowledgeService


class ConversationService:
    """Manages conversations, message persistence, context building, and reply triggers."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ConversationRepository(db)
        self.account_repo = AccountRepository(db)
        self.knowledge_service = KnowledgeService(db)

    # ── Contact & Conversation Discovery ───────────────────────────

    def get_or_create_contact(
        self,
        account_id: str,
        platform_contact_id: str,
        display_name: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> Contact:
        """Find or create a contact strictly scoped to an account."""
        contact = self.repo.get_contact_by_platform_id(account_id, platform_contact_id)
        if not contact:
            contact = Contact(
                account_id=account_id,
                platform_contact_id=platform_contact_id,
                display_name=display_name or platform_contact_id,
                phone_number=phone_number,
            )
            contact = self.repo.create_contact(contact)
        else:
            # Update last seen
            contact.last_seen_at = datetime.now(timezone.utc)
            if display_name and contact.display_name != display_name:
                contact.display_name = display_name
            self.repo.update_contact(contact)

        return contact

    def get_or_create_conversation(
        self,
        account_id: str,
        contact_id: str,
        platform_conversation_id: Optional[str] = None,
    ) -> Conversation:
        """Retrieve existing thread or initialize a new conversation."""
        conv = self.repo.get_conversation_by_contact(account_id, contact_id)
        if not conv:
            conv = Conversation(
                account_id=account_id,
                contact_id=contact_id,
                platform_conversation_id=platform_conversation_id,
                status="active",
                message_count=0,
                last_message_at=datetime.now(timezone.utc),
            )
            conv = self.repo.create_conversation(conv)
        return conv

    def get_conversation_or_404(
        self, conversation_id: str, load_messages: bool = True
    ) -> Conversation:
        """Fetch conversation by ID or raise 404."""
        conv = self.repo.get_conversation_by_id(conversation_id, load_messages=load_messages)
        if not conv:
            raise NotFoundException(f"Conversation '{conversation_id}' not found.")
        return conv

    def list_conversations(
        self,
        account_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Conversation]:
        """List conversations with optional filters."""
        return self.repo.list_conversations(
            account_id=account_id, status=status, limit=limit, offset=offset
        )

    # ── Message Recording ──────────────────────────────────────────

    def record_message(
        self,
        conversation_id: str,
        data: MessageCreate,
    ) -> Message:
        """Persist a message and update conversation metadata."""
        conv = self.get_conversation_or_404(conversation_id, load_messages=False)

        msg = Message(
            conversation_id=conversation_id,
            account_id=conv.account_id,
            platform_message_id=data.platform_message_id,
            direction=data.direction,
            content=data.content,
            message_type=data.message_type,
            sender_type=data.sender_type,
            ai_metadata=data.ai_metadata,
            delivery_status=data.delivery_status,
            is_ai_generated=data.is_ai_generated,
            owner_approved=data.owner_approved,
        )
        saved = self.repo.create_message(msg)

        # Update conversation stats
        conv.message_count += 1
        conv.last_message_at = datetime.now(timezone.utc)
        self.repo.update_conversation(conv)

        return saved

    def get_conversation_context(
        self, conversation_id: str, limit: int = 15
    ) -> list[MessageHistoryItem]:
        """Retrieve recent chronological history formatted for the AI prompt."""
        recent_messages = self.repo.get_recent_messages(conversation_id, limit=limit)
        items = []
        for m in recent_messages:
            role = "assistant" if m.direction == "outbound" else "user"
            items.append(MessageHistoryItem(role=role, content=m.content))
        return items

    # ── AI Generation on Conversation Thread ───────────────────────

    def generate_reply_for_conversation(
        self,
        conversation_id: str,
        auto_save_outbound: bool = False,
        custom_instruction: Optional[str] = None,
    ) -> AIResponsePayload:
        """
        Generate an AI reply using the conversation's real context history
        and the account's personality + verified business knowledge.
        """
        conv = self.get_conversation_or_404(conversation_id, load_messages=True)
        account = self.account_repo.get_by_id(conv.account_id)
        if not account:
            raise NotFoundException(f"Account for conversation '{conversation_id}' not found.")

        # Context history
        history = self.get_conversation_context(
            conversation_id, limit=account.context_window_size
        )

        # Get latest inbound message as trigger prompt
        last_inbound = next(
            (m for m in reversed(conv.messages) if m.direction == "inbound"), None
        )
        message_text = last_inbound.content if last_inbound else "Hello"

        # Verified business knowledge
        business_context = self.knowledge_service.compile_knowledge_for_account(account.id)

        gen_req = GenerateReplyRequest(
            account_id=account.id,
            message=message_text,
            sender_name=conv.contact.display_name if conv.contact else None,
            conversation_history=history[:-1] if history else [],
            business_context=business_context,
        )

        engine = AIEngine()
        response_payload = engine.process_message(account=account, request=gen_req)

        # Save outbound message if requested and not blocked
        if auto_save_outbound:
            self.record_message(
                conversation_id=conversation_id,
                data=MessageCreate(
                    content=response_payload.reply,
                    direction="outbound",
                    sender_type="assistant",
                    delivery_status="sent",
                    is_ai_generated=True,
                    owner_approved=not response_payload.requires_human,
                    ai_metadata=response_payload.model_dump(),
                ),
            )

        return response_payload

    # ── Manual Assisted Workflow for Personal Accounts ─────────────

    def handle_manual_message(
        self,
        req: ManualMessageRequest,
    ) -> ManualMessageResponse:
        """
        AI-Assisted manual workflow for Personal Accounts:
        1. Identifies the personal account.
        2. Retrieves or registers the contact.
        3. Retrieves or creates conversation thread.
        4. Persists the pasted incoming message.
        5. Generates the reply matching Aashray's casual Hinglish persona.
        6. Returns copyable reply for the dashboard.
        """
        account = self.account_repo.get_by_id(req.account_id)
        if not account:
            raise NotFoundException(f"Account '{req.account_id}' not found.")

        # 1. Contact & Conversation
        contact = self.get_or_create_contact(
            account_id=account.id,
            platform_contact_id=req.sender_contact_id,
            display_name=req.sender_name,
        )
        conv = self.get_or_create_conversation(account_id=account.id, contact_id=contact.id)

        # 2. Record incoming message
        if req.record_in_history:
            self.record_message(
                conversation_id=conv.id,
                data=MessageCreate(
                    content=req.message_content,
                    direction="inbound",
                    sender_type="contact",
                    delivery_status="received",
                    is_ai_generated=False,
                ),
            )

        # 3. Retrieve context history
        history = self.get_conversation_context(conv.id, limit=account.context_window_size)

        # 4. Generate candidate reply
        gen_req = GenerateReplyRequest(
            account_id=account.id,
            message=req.message_content,
            sender_name=contact.display_name,
            conversation_history=history[:-1] if history else [],
        )

        engine = AIEngine()
        reply_payload = engine.process_message(account=account, request=gen_req)

        return ManualMessageResponse(
            conversation_id=conv.id,
            contact_id=contact.id,
            incoming_message=req.message_content,
            suggested_reply=reply_payload,
            copyable_text=reply_payload.reply,
        )

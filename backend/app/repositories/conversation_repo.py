"""
Repository for Contact, Conversation, and Message persistence and queries.
"""

from typing import Optional, Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.contact import Contact
from app.models.conversation import Conversation
from app.models.message import Message


class ConversationRepository:
    """Manages conversations, contacts, and message history with strict account scoping."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Contacts ───────────────────────────────────────────────────

    def get_contact_by_platform_id(
        self, account_id: str, platform_contact_id: str
    ) -> Optional[Contact]:
        """Lookup a contact strictly scoped to an account."""
        stmt = (
            select(Contact)
            .where(
                Contact.account_id == account_id,
                Contact.platform_contact_id == platform_contact_id,
            )
        )
        return self.db.scalars(stmt).first()

    def create_contact(self, contact: Contact) -> Contact:
        """Create and persist a new contact."""
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def update_contact(self, contact: Contact) -> Contact:
        """Save updates to a contact."""
        self.db.commit()
        self.db.refresh(contact)
        return contact

    # ── Conversations ──────────────────────────────────────────────

    def get_conversation_by_id(
        self, conversation_id: str, load_messages: bool = False
    ) -> Optional[Conversation]:
        """Retrieve conversation by ID with optional messages eager load."""
        stmt = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.contact))
        )
        if load_messages:
            stmt = stmt.options(selectinload(Conversation.messages))
        return self.db.scalars(stmt).first()

    def get_conversation_by_contact(
        self, account_id: str, contact_id: str
    ) -> Optional[Conversation]:
        """Retrieve the primary conversation thread between an account and a contact."""
        stmt = (
            select(Conversation)
            .where(
                Conversation.account_id == account_id,
                Conversation.contact_id == contact_id,
            )
            .options(selectinload(Conversation.contact))
        )
        return self.db.scalars(stmt).first()

    def list_conversations(
        self,
        account_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Conversation]:
        """List conversations with optional filters."""
        stmt = (
            select(Conversation)
            .options(selectinload(Conversation.contact))
            .order_by(Conversation.last_message_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if account_id:
            stmt = stmt.where(Conversation.account_id == account_id)
        if status:
            stmt = stmt.where(Conversation.status == status)

        return self.db.scalars(stmt).all()

    def create_conversation(self, conversation: Conversation) -> Conversation:
        """Persist a new conversation."""
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def update_conversation(self, conversation: Conversation) -> Conversation:
        """Save updates to a conversation."""
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    # ── Messages ───────────────────────────────────────────────────

    def create_message(self, message: Message) -> Message:
        """Persist a message and increment parent conversation message count."""
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_message_by_platform_id(
        self, platform_message_id: str
    ) -> Optional[Message]:
        """Find an existing message by platform ID for duplicate detection."""
        stmt = select(Message).where(Message.platform_message_id == platform_message_id)
        return self.db.scalars(stmt).first()

    def get_recent_messages(
        self, conversation_id: str, limit: int = 15
    ) -> list[Message]:
        """Fetch the most recent N messages for context building (in chronological order)."""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        recent_desc = self.db.scalars(stmt).all()
        # Return in ascending chronological order for LLM context
        return list(reversed(recent_desc))

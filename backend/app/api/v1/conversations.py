"""
API endpoints for Conversations, Message History, and Manual Workflows.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.ai.schemas import AIResponsePayload
from app.api.deps import get_db
from app.schemas.conversation import (
    ConversationDetailRead,
    ConversationRead,
    ConversationReplyRequest,
    ManualMessageRequest,
    ManualMessageResponse,
    MessageCreate,
    MessageRead,
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations & Memory"])


@router.get("", response_model=list[ConversationRead])
def list_conversations(
    account_id: Optional[str] = Query(None, description="Filter by account"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[ConversationRead]:
    """List conversation threads with optional account filtering."""
    service = ConversationService(db)
    conversations = service.list_conversations(
        account_id=account_id, status=status_filter, limit=limit, offset=offset
    )
    return [ConversationRead.model_validate(c) for c in conversations]


@router.get("/{conversation_id}", response_model=ConversationDetailRead)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
) -> ConversationDetailRead:
    """Retrieve full conversation details including messages."""
    service = ConversationService(db)
    conv = service.get_conversation_or_404(conversation_id, load_messages=True)
    return ConversationDetailRead.model_validate(conv)


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[MessageRead]:
    """Retrieve message history for a specific conversation."""
    service = ConversationService(db)
    service.get_conversation_or_404(conversation_id, load_messages=False)
    messages = service.repo.get_recent_messages(conversation_id, limit=limit)
    return [MessageRead.model_validate(m) for m in messages]


@router.post("/{conversation_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def add_message(
    conversation_id: str,
    data: MessageCreate,
    db: Session = Depends(get_db),
) -> MessageRead:
    """Manually append a message to an existing conversation thread."""
    service = ConversationService(db)
    msg = service.record_message(conversation_id, data)
    return MessageRead.model_validate(msg)


@router.post("/{conversation_id}/reply", response_model=AIResponsePayload)
def generate_conversation_reply(
    conversation_id: str,
    req: ConversationReplyRequest,
    db: Session = Depends(get_db),
) -> AIResponsePayload:
    """
    Generate an AI reply using the conversation's real context history
    and account personality.
    """
    service = ConversationService(db)
    return service.generate_reply_for_conversation(
        conversation_id=conversation_id,
        auto_save_outbound=req.auto_save_outbound,
        custom_instruction=req.custom_instruction,
    )


@router.post("/manual-input", response_model=ManualMessageResponse)
def handle_manual_input(
    req: ManualMessageRequest,
    db: Session = Depends(get_db),
) -> ManualMessageResponse:
    """
    AI-assisted workflow for Personal WhatsApp / Instagram:
    Owner pastes incoming message, AI generates reply matching Aashray's persona,
    and returns copyable text.
    """
    service = ConversationService(db)
    return service.handle_manual_message(req)


"""
API endpoints for Dashboard Metrics, Live Analytics, and Approvals.
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.account import Account
from app.models.audit_log import AuditLog
from app.models.message import Message

router = APIRouter(tags=["Analytics & Approvals"])


class MetricSummaryRead(BaseModel):
    connected_accounts: int
    messages_received: int
    messages_handled: int
    pending_approvals: int
    auto_reply_rate: int


class RecentActivityItemRead(BaseModel):
    id: str
    account_id: str
    account_name: str
    platform: str
    account_type: str
    event_type: str
    description: str
    snippet: Optional[str] = None
    timestamp: str
    status: str


class ApprovalRead(BaseModel):
    id: str
    conversation_id: str
    account_id: str
    account_name: str
    platform: str
    account_type: str
    customer_name: str
    incoming_message: str
    proposed_reply: str
    intent: str
    confidence: float
    status: str
    created_at: str
    reason: Optional[str] = None


@router.get("/metrics", response_model=MetricSummaryRead)
def get_metrics_summary(db: Session = Depends(get_db)) -> MetricSummaryRead:
    """Retrieve aggregate statistics across all connected channels."""
    connected_count = (
        db.query(Account).filter(Account.integration_status == "connected").count()
    )
    inbound_count = (
        db.query(Message).filter(Message.direction == "inbound").count()
    )
    outbound_count = (
        db.query(Message).filter(Message.direction == "outbound").count()
    )
    pending_count = (
        db.query(Message)
        .filter(Message.is_ai_generated.is_(True), Message.owner_approved.is_(False))
        .count()
    )
    ai_auto_count = (
        db.query(Message)
        .filter(Message.is_ai_generated.is_(True), Message.owner_approved.is_(True))
        .count()
    )

    auto_reply_rate = (
        round((ai_auto_count / max(inbound_count, 1)) * 100)
        if inbound_count > 0
        else 0
    )

    return MetricSummaryRead(
        connected_accounts=connected_count,
        messages_received=inbound_count,
        messages_handled=outbound_count,
        pending_approvals=pending_count,
        auto_reply_rate=auto_reply_rate,
    )


@router.get("/recent-activity", response_model=list[RecentActivityItemRead])
def get_recent_activity(
    limit: int = 15, db: Session = Depends(get_db)
) -> list[RecentActivityItemRead]:
    """Retrieve recent communication events and system actions."""
    # 1. Fetch recent audit logs
    logs = (
        db.query(AuditLog)
        .order_by(desc(AuditLog.created_at))
        .limit(limit)
        .all()
    )

    activities: list[RecentActivityItemRead] = []
    for log in logs:
        account_name = "System"
        platform = "system"
        account_type = "system"
        if log.account:
            account_name = log.account.display_name
            platform = log.account.platform
            account_type = log.account.account_type

        status_flag = "success"
        if "escalated" in log.action or "emergency" in log.action:
            status_flag = "warning"
        elif "pending" in log.action or "approval" in log.action:
            status_flag = "pending"

        snippet = None
        if isinstance(log.details, dict):
            snippet = log.details.get("reason") or log.details.get("content") or log.details.get("intent")

        activities.append(
            RecentActivityItemRead(
                id=log.id,
                account_id=log.account_id or "system",
                account_name=account_name,
                platform=platform,
                account_type=account_type,
                event_type=log.action,
                description=f"{account_name} — {log.action.replace('_', ' ').title()}",
                snippet=str(snippet) if snippet else None,
                timestamp=log.created_at.isoformat(),
                status=status_flag,
            )
        )

    # 2. If no audit logs yet, synthesize from recent messages
    if not activities:
        recent_messages = (
            db.query(Message)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .all()
        )
        for msg in recent_messages:
            acc = msg.account
            acc_name = acc.display_name if acc else "Account"
            plat = acc.platform if acc else "whatsapp"
            acct_type = acc.account_type if acc else "personal"

            event_type = "auto_reply" if msg.is_ai_generated else ("inbound" if msg.direction == "inbound" else "approved")
            activities.append(
                RecentActivityItemRead(
                    id=msg.id,
                    account_id=msg.account_id,
                    account_name=acc_name,
                    platform=plat,
                    account_type=acct_type,
                    event_type=event_type,
                    description=f"{'Received from' if msg.direction == 'inbound' else 'Sent to'} contact",
                    snippet=msg.content[:80],
                    timestamp=msg.created_at.isoformat(),
                    status="live" if msg.direction == "inbound" else "success",
                )
            )

    return activities


@router.get("/approvals", response_model=list[ApprovalRead])
def get_pending_approvals(db: Session = Depends(get_db)) -> list[ApprovalRead]:
    """Retrieve all draft AI responses waiting for owner confirmation."""
    pending_messages = (
        db.query(Message)
        .filter(Message.is_ai_generated.is_(True), Message.owner_approved.is_(False))
        .order_by(desc(Message.created_at))
        .all()
    )

    approvals: list[ApprovalRead] = []
    for msg in pending_messages:
        acc = msg.account
        acc_name = acc.display_name if acc else "Account"
        plat = acc.platform if acc else "whatsapp"
        acct_type = acc.account_type if acc else "business"

        conv = msg.conversation
        cust_name = conv.contact.display_name if conv and conv.contact else "Customer"

        # Find preceding inbound message
        prev_inbound = (
            db.query(Message)
            .filter(
                Message.conversation_id == msg.conversation_id,
                Message.direction == "inbound",
            )
            .order_by(desc(Message.created_at))
            .first()
        )
        incoming_text = prev_inbound.content if prev_inbound else "Incoming message"

        ai_meta = msg.ai_metadata or {}
        intent = ai_meta.get("intent", "general_enquiry")
        conf = float(ai_meta.get("confidence", 0.85))
        reason = ai_meta.get("reason") or ai_meta.get("policy_reason")

        approvals.append(
            ApprovalRead(
                id=msg.id,
                conversation_id=msg.conversation_id,
                account_id=msg.account_id,
                account_name=acc_name,
                platform=plat,
                account_type=acct_type,
                customer_name=cust_name,
                incoming_message=incoming_text,
                proposed_reply=msg.content,
                intent=intent,
                confidence=conf,
                status="pending",
                created_at=msg.created_at.isoformat(),
                reason=reason,
            )
        )

    return approvals


@router.post("/approvals/{approval_id}/approve")
def approve_pending_message(approval_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Approve a draft AI message and dispatch it to the platform."""
    msg = db.query(Message).filter(Message.id == approval_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Approval item not found")

    msg.owner_approved = True
    msg.delivery_status = "sent"
    db.commit()

    # Log action to audit log
    audit = AuditLog(
        account_id=msg.account_id,
        action="manual_approved",
        resource_type="message",
        resource_id=msg.id,
        details={"approved_by": "owner", "content": msg.content},
    )
    db.add(audit)
    db.commit()

    return {"status": "approved", "message_id": msg.id}


@router.post("/approvals/{approval_id}/reject")
def reject_pending_message(approval_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Reject and cancel a draft AI message."""
    msg = db.query(Message).filter(Message.id == approval_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Approval item not found")

    msg.delivery_status = "failed"
    db.delete(msg)
    db.commit()

    # Log rejection
    audit = AuditLog(
        account_id=msg.account_id,
        action="manual_rejected",
        resource_type="message",
        resource_id=msg.id,
        details={"rejected_by": "owner"},
    )
    db.add(audit)
    db.commit()

    return {"status": "rejected", "message_id": approval_id}

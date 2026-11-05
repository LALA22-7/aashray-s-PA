"""
Repositories for AuditLog, WebhookEvent (idempotency), and Lead tracking.
"""

from datetime import datetime, timezone
from typing import Any, Optional, Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.lead import Lead
from app.models.webhook_event import WebhookEvent


class AuditLogRepository:
    """Manages system audit entries."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def log(
        self,
        action: str,
        account_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Create and persist an immutable audit record."""
        entry = AuditLog(
            account_id=account_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def list_logs(
        self,
        account_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AuditLog]:
        """Fetch audit logs ordered by recency."""
        stmt = select(AuditLog).order_by(desc(AuditLog.created_at)).offset(offset).limit(limit)
        if account_id:
            stmt = stmt.where(AuditLog.account_id == account_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        return self.db.scalars(stmt).all()


class WebhookEventRepository:
    """Manages raw webhook records and guarantees event idempotency."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_platform_event_id(self, platform_event_id: str) -> Optional[WebhookEvent]:
        """Lookup by unique external ID to prevent duplicate event execution."""
        stmt = select(WebhookEvent).where(WebhookEvent.platform_event_id == platform_event_id)
        return self.db.scalars(stmt).first()

    def record_event(
        self,
        platform: str,
        event_type: str,
        platform_event_id: str,
        raw_payload: dict[str, Any],
        account_id: Optional[str] = None,
    ) -> WebhookEvent:
        """Store incoming raw event."""
        event = WebhookEvent(
            account_id=account_id,
            platform=platform,
            event_type=event_type,
            platform_event_id=platform_event_id,
            raw_payload=raw_payload,
            processing_status="received",
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def mark_processed(
        self, event: WebhookEvent, status: str = "processed", error: Optional[str] = None
    ) -> WebhookEvent:
        """Update processing status upon completion."""
        event.processing_status = status
        event.error_message = error
        event.processed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_events(
        self,
        account_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[WebhookEvent]:
        """Fetch webhook events."""
        stmt = (
            select(WebhookEvent)
            .order_by(desc(WebhookEvent.created_at))
            .offset(offset)
            .limit(limit)
        )
        if account_id:
            stmt = stmt.where(WebhookEvent.account_id == account_id)
        if status:
            stmt = stmt.where(WebhookEvent.processing_status == status)
        return self.db.scalars(stmt).all()


class LeadRepository:
    """Manages business leads captured from conversations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, lead_id: str) -> Optional[Lead]:
        """Find lead by UUID."""
        stmt = select(Lead).where(Lead.id == lead_id)
        return self.db.scalars(stmt).first()

    def get_by_conversation_id(self, conversation_id: str) -> Optional[Lead]:
        """Find existing lead attached to a conversation thread."""
        stmt = select(Lead).where(Lead.conversation_id == conversation_id)
        return self.db.scalars(stmt).first()

    def create(self, lead: Lead) -> Lead:
        """Create a new lead."""
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def update(self, lead: Lead) -> Lead:
        """Update lead status or notes."""
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def list_leads(
        self,
        account_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Lead]:
        """List captured leads."""
        stmt = select(Lead).order_by(desc(Lead.created_at)).offset(offset).limit(limit)
        if account_id:
            stmt = stmt.where(Lead.account_id == account_id)
        if status:
            stmt = stmt.where(Lead.status == status)
        return self.db.scalars(stmt).all()


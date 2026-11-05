"""
API endpoints for Audit Logs, Captured Leads, and Webhook Event inspection.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import NotFoundException
from app.schemas.safety import (
    AuditLogRead,
    LeadRead,
    LeadStatus,
    LeadUpdate,
    WebhookEventRead,
)
from app.services.safety_service import SafetyService

router = APIRouter(tags=["Safety, Audits & Leads"])


@router.get("/audit-logs", response_model=list[AuditLogRead])
def list_audit_logs(
    account_id: Optional[str] = Query(None, description="Filter by account"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[AuditLogRead]:
    """Retrieve system audit logs for policy decisions and state changes."""
    service = SafetyService(db)
    logs = service.audit_repo.list_logs(
        account_id=account_id, action=action, limit=limit, offset=offset
    )
    return [AuditLogRead.model_validate(log) for log in logs]


@router.get("/leads", response_model=list[LeadRead])
def list_leads(
    account_id: Optional[str] = Query(None, description="Filter by account"),
    status: Optional[LeadStatus] = Query(None, description="Filter by lead status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[LeadRead]:
    """Retrieve advertising campaign prospects qualified by AI."""
    service = SafetyService(db)
    leads = service.lead_repo.list_leads(
        account_id=account_id,
        status=status.value if status else None,
        limit=limit,
        offset=offset,
    )
    return [LeadRead.model_validate(lead) for lead in leads]


@router.get("/leads/{lead_id}", response_model=LeadRead)
def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
) -> LeadRead:
    """Fetch a single lead by ID."""
    service = SafetyService(db)
    lead = service.lead_repo.get_by_id(lead_id)
    if not lead:
        raise NotFoundException(f"Lead '{lead_id}' not found.")
    return LeadRead.model_validate(lead)


@router.patch("/leads/{lead_id}", response_model=LeadRead)
def update_lead(
    lead_id: str,
    data: LeadUpdate,
    db: Session = Depends(get_db),
) -> LeadRead:
    """Update lead status, follow-up notes, or campaign quantity."""
    service = SafetyService(db)
    lead = service.lead_repo.get_by_id(lead_id)
    if not lead:
        raise NotFoundException(f"Lead '{lead_id}' not found.")

    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if hasattr(lead, field) and value is not None:
            if hasattr(value, "value"):  # Enum
                setattr(lead, field, value.value)
            else:
                setattr(lead, field, value)

    updated = service.lead_repo.update(lead)
    return LeadRead.model_validate(updated)


@router.get("/webhook-events", response_model=list[WebhookEventRead])
def list_webhook_events(
    account_id: Optional[str] = Query(None, description="Filter by account"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[WebhookEventRead]:
    """Inspect raw incoming webhook events for debugging and idempotency tracing."""
    service = SafetyService(db)
    events = service.webhook_repo.list_events(
        account_id=account_id, status=status, limit=limit, offset=offset
    )
    return [WebhookEventRead.model_validate(e) for e in events]

"""
API endpoints for managing Accounts and Personality configurations.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import AccountType, PlatformType
from app.schemas.account import (
    AccountConnectRequest,
    AccountCreate,
    AccountDetailRead,
    AccountRead,
    AccountUpdate,
)
from app.schemas.personality import PersonalityConfigRead, PersonalityConfigUpdate
from app.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=list[AccountRead])
def list_accounts(
    platform: Optional[PlatformType] = Query(None, description="Filter by platform"),
    account_type: Optional[AccountType] = Query(None, description="Filter by account type"),
    db: Session = Depends(get_db),
) -> list[AccountRead]:
    """Retrieve all managed communication accounts."""
    service = AccountService(db)
    accounts = service.list_accounts(
        platform=platform.value if platform else None,
        account_type=account_type.value if account_type else None,
    )
    return [service.to_account_read(acc) for acc in accounts]


@router.post("", response_model=AccountDetailRead, status_code=status.HTTP_201_CREATED)
def create_account(
    data: AccountCreate,
    db: Session = Depends(get_db),
) -> AccountDetailRead:
    """Register a new communication account."""
    service = AccountService(db)
    account = service.create_account(data)
    return service.to_account_detail_read(account)


@router.post("/seed", response_model=list[AccountDetailRead])
def seed_default_accounts(
    db: Session = Depends(get_db),
) -> list[AccountDetailRead]:
    """Initialize the four foundational accounts (WhatsApp & Instagram, Personal & Business)."""
    service = AccountService(db)
    service.seed_default_accounts()
    all_accounts = service.list_accounts()
    return [service.to_account_detail_read(acc) for acc in all_accounts]


@router.get("/{account_id}", response_model=AccountDetailRead)
def get_account(
    account_id: str,
    db: Session = Depends(get_db),
) -> AccountDetailRead:
    """Retrieve detailed account information including personality profile."""
    service = AccountService(db)
    account = service.get_account_or_404(account_id)
    return service.to_account_detail_read(account)


@router.patch("/{account_id}", response_model=AccountRead)
def update_account(
    account_id: str,
    data: AccountUpdate,
    db: Session = Depends(get_db),
) -> AccountRead:
    """Update settings or operational flags on an account."""
    service = AccountService(db)
    account = service.update_account(account_id, data)
    return service.to_account_read(account)


@router.post("/{account_id}/connect", response_model=AccountRead)
def connect_account(
    account_id: str,
    req: AccountConnectRequest,
    db: Session = Depends(get_db),
) -> AccountRead:
    """Store encrypted integration credentials and mark account connected."""
    service = AccountService(db)
    account = service.connect_account(account_id, req)
    return service.to_account_read(account)


@router.post("/{account_id}/disconnect", response_model=AccountRead)
def disconnect_account(
    account_id: str,
    db: Session = Depends(get_db),
) -> AccountRead:
    """Revoke credentials, halt automation, and mark account disconnected."""
    service = AccountService(db)
    account = service.disconnect_account(account_id)
    return service.to_account_read(account)


# ── Personality Endpoints ──────────────────────────────────────────

@router.get("/{account_id}/personality", response_model=PersonalityConfigRead)
def get_account_personality(
    account_id: str,
    db: Session = Depends(get_db),
) -> PersonalityConfigRead:
    """Fetch the specific personality and tone profile of an account."""
    service = AccountService(db)
    personality = service.get_personality(account_id)
    return PersonalityConfigRead.model_validate(personality)


@router.patch("/{account_id}/personality", response_model=PersonalityConfigRead)
def update_account_personality(
    account_id: str,
    data: PersonalityConfigUpdate,
    db: Session = Depends(get_db),
) -> PersonalityConfigRead:
    """Modify tone, reply length, humor, Hinglish, or formality of an account's AI persona."""
    service = AccountService(db)
    personality = service.update_personality(account_id, data)
    return PersonalityConfigRead.model_validate(personality)

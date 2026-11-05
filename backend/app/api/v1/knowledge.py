"""
API endpoints for managing the Business Knowledge Base.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.knowledge import (
    BusinessKnowledgeCreate,
    BusinessKnowledgeRead,
    BusinessKnowledgeUpdate,
    KnowledgeCategory,
    KnowledgeSummaryResponse,
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["Business Knowledge Base"])


@router.get("", response_model=list[BusinessKnowledgeRead])
def list_knowledge(
    account_id: Optional[str] = Query(None, description="Filter by account"),
    category: Optional[KnowledgeCategory] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
) -> list[BusinessKnowledgeRead]:
    """Retrieve all business knowledge entries with optional filters."""
    service = KnowledgeService(db)
    items = service.list_knowledge(
        account_id=account_id,
        category=category.value if category else None,
        is_active=is_active,
    )
    return [BusinessKnowledgeRead.model_validate(i) for i in items]


@router.post("", response_model=BusinessKnowledgeRead, status_code=status.HTTP_201_CREATED)
def create_knowledge(
    data: BusinessKnowledgeCreate,
    db: Session = Depends(get_db),
) -> BusinessKnowledgeRead:
    """Create a new fact, FAQ, or package in the knowledge base."""
    service = KnowledgeService(db)
    item = service.create_knowledge(data)
    return BusinessKnowledgeRead.model_validate(item)


@router.post("/seed", response_model=dict)
def seed_default_knowledge(db: Session = Depends(get_db)) -> dict:
    """Seed initial verified bottle advertising agency knowledge items."""
    service = KnowledgeService(db)
    seeded_count = service.seed_default_knowledge()
    return {"status": "success", "seeded_count": seeded_count}


@router.get("/summary", response_model=KnowledgeSummaryResponse)
def get_knowledge_summary(
    account_id: Optional[str] = Query(None, description="Optional account scope"),
    db: Session = Depends(get_db),
) -> KnowledgeSummaryResponse:
    """Preview compiled facts and categories active in the knowledge base."""
    service = KnowledgeService(db)
    items = service.list_knowledge(account_id=account_id)
    active_items = [i for i in items if i.is_active]
    categories = sorted(list({i.category for i in items}))
    preview = service.compile_knowledge_for_account(account_id or "")

    return KnowledgeSummaryResponse(
        total_items=len(items),
        active_items=len(active_items),
        categories_present=categories,
        compiled_preview=preview,
    )


@router.get("/{knowledge_id}", response_model=BusinessKnowledgeRead)
def get_knowledge(
    knowledge_id: str,
    db: Session = Depends(get_db),
) -> BusinessKnowledgeRead:
    """Fetch single knowledge item by ID."""
    service = KnowledgeService(db)
    item = service.get_knowledge_or_404(knowledge_id)
    return BusinessKnowledgeRead.model_validate(item)


@router.patch("/{knowledge_id}", response_model=BusinessKnowledgeRead)
def update_knowledge(
    knowledge_id: str,
    data: BusinessKnowledgeUpdate,
    db: Session = Depends(get_db),
) -> BusinessKnowledgeRead:
    """Update an existing knowledge item."""
    service = KnowledgeService(db)
    item = service.update_knowledge(knowledge_id, data)
    return BusinessKnowledgeRead.model_validate(item)


@router.delete("/{knowledge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge(
    knowledge_id: str,
    db: Session = Depends(get_db),
) -> None:
    """Delete a knowledge item."""
    service = KnowledgeService(db)
    service.delete_knowledge(knowledge_id)

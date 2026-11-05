"""
Repository for BusinessKnowledge persistence and queries.
"""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.business_knowledge import BusinessKnowledge


class KnowledgeRepository:
    """Handles CRUD queries for BusinessKnowledge items."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, knowledge_id: str) -> Optional[BusinessKnowledge]:
        """Fetch a knowledge item by its UUID."""
        stmt = select(BusinessKnowledge).where(BusinessKnowledge.id == knowledge_id)
        return self.db.scalars(stmt).first()

    def get_all(
        self,
        account_id: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> Sequence[BusinessKnowledge]:
        """
        Fetch knowledge items with optional filtering.
        If account_id is given, returns items specific to that account OR shared items (account_id IS NULL).
        """
        stmt = select(BusinessKnowledge).order_by(
            BusinessKnowledge.priority.desc(), BusinessKnowledge.created_at
        )

        if account_id:
            stmt = stmt.where(
                (BusinessKnowledge.account_id == account_id)
                | (BusinessKnowledge.account_id.is_(None))
            )
        if category:
            stmt = stmt.where(BusinessKnowledge.category == category)
        if is_active is not None:
            stmt = stmt.where(BusinessKnowledge.is_active == is_active)
        if limit:
            stmt = stmt.limit(limit)

        return self.db.scalars(stmt).all()

    def create(self, knowledge: BusinessKnowledge) -> BusinessKnowledge:
        """Insert a new knowledge item."""
        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)
        return knowledge

    def update(self, knowledge: BusinessKnowledge) -> BusinessKnowledge:
        """Update an existing knowledge item."""
        self.db.commit()
        self.db.refresh(knowledge)
        return knowledge

    def delete(self, knowledge: BusinessKnowledge) -> None:
        """Delete a knowledge item."""
        self.db.delete(knowledge)
        self.db.commit()

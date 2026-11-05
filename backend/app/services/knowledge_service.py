"""
Service for managing the Business Knowledge Base and compiling context for the AI Engine.
"""

from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.business_knowledge import BusinessKnowledge
from app.repositories.knowledge_repo import KnowledgeRepository
from app.schemas.knowledge import (
    BusinessKnowledgeCreate,
    BusinessKnowledgeUpdate,
    KnowledgeCategory,
)


class KnowledgeService:
    """Handles business facts, bottle advertising services, FAQs, and prompt compilation."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = KnowledgeRepository(db)

    def create_knowledge(self, data: BusinessKnowledgeCreate) -> BusinessKnowledge:
        """Create a new business knowledge entry."""
        item = BusinessKnowledge(
            account_id=data.account_id,
            category=data.category.value,
            title=data.title,
            content=data.content,
            is_active=data.is_active,
            priority=data.priority,
            knowledge_metadata=data.knowledge_metadata,
        )
        return self.repo.create(item)

    def get_knowledge_or_404(self, knowledge_id: str) -> BusinessKnowledge:
        """Retrieve knowledge item or raise 404."""
        item = self.repo.get_by_id(knowledge_id)
        if not item:
            raise NotFoundException(f"Knowledge item '{knowledge_id}' not found.")
        return item

    def list_knowledge(
        self,
        account_id: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Sequence[BusinessKnowledge]:
        """Fetch filtered knowledge items."""
        return self.repo.get_all(account_id=account_id, category=category, is_active=is_active)

    def update_knowledge(
        self, knowledge_id: str, data: BusinessKnowledgeUpdate
    ) -> BusinessKnowledge:
        """Update a knowledge entry."""
        item = self.get_knowledge_or_404(knowledge_id)

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(item, field) and value is not None:
                if hasattr(value, "value"):  # Enum support
                    setattr(item, field, value.value)
                else:
                    setattr(item, field, value)

        return self.repo.update(item)

    def delete_knowledge(self, knowledge_id: str) -> None:
        """Delete a knowledge entry."""
        item = self.get_knowledge_or_404(knowledge_id)
        self.repo.delete(item)

    def compile_knowledge_for_account(self, account_id: str) -> str:
        """
        Compile all active business knowledge items relevant to this account into
        a well-structured text block for the AI system prompt.
        """
        items = self.repo.get_all(account_id=account_id, is_active=True)
        if not items:
            return ""

        lines = []
        for item in items:
            lines.append(f"[{item.category.upper()}] {item.title}: {item.content}")

        return "\n".join(lines)

    def seed_default_knowledge(self) -> int:
        """
        Seed initial verified facts for Aashray's Bottle Advertising Agency.
        Idempotent: skips if knowledge base is not empty.
        """
        existing = self.repo.get_all(limit=1)
        if existing:
            return 0

        default_entries = [
            BusinessKnowledgeCreate(
                category=KnowledgeCategory.AGENCY_INFO,
                title="Agency Overview",
                content="Aashray's Bottle Advertising Agency specializes in high-impact brand promotions using custom printed, labeled, or sleeve-wrapped water and beverage bottles distributed at events, corporate hubs, and high-footfall venues.",
                priority=100,
            ),
            BusinessKnowledgeCreate(
                category=KnowledgeCategory.SERVICE,
                title="Bottle Advertising Formats",
                content="We provide 3 primary formats: (1) Full-body shrink sleeves (360-degree branding), (2) Custom high-gloss waterproof labels on premium bottles, (3) Eco-friendly paper-wrapped bottles for corporate green events.",
                priority=90,
            ),
            BusinessKnowledgeCreate(
                category=KnowledgeCategory.MOQ,
                title="Minimum Order Quantities",
                content="Standard minimum order quantity (MOQ) is 500 bottles. For high-volume campaigns (5,000+ to 50,000+ units), custom tier discounts apply.",
                priority=85,
            ),
            BusinessKnowledgeCreate(
                category=KnowledgeCategory.PRICING,
                title="Pricing Structure",
                content="Pricing is volume-dependent and customized per campaign. Indicative pricing starts from ₹18 - ₹35 per bottle depending on bottle size (250ml, 500ml, 1L), label finish, and delivery city. Exact quote requires bottle count and delivery location.",
                priority=80,
            ),
            BusinessKnowledgeCreate(
                category=KnowledgeCategory.LOCATION,
                title="Target Campaign Locations",
                content="We operate primarily across Mumbai, Pune, Delhi NCR, Bangalore, and Hyderabad. Pan-India distribution is available for bulk corporate orders.",
                priority=75,
            ),
            BusinessKnowledgeCreate(
                category=KnowledgeCategory.DELIVERY_TIMELINE,
                title="Production & Delivery Timelines",
                content="Standard turnaround is 7 to 10 working days post design artwork sign-off. Express 3-day turnaround is available for urgent events upon request.",
                priority=70,
            ),
            BusinessKnowledgeCreate(
                category=KnowledgeCategory.FAQ,
                title="Design Assistance FAQ",
                content="Do we design labels? Yes, clients can provide their ready artwork or our in-house design team can assist with 3D mockups and bottle label layouts.",
                priority=60,
            ),
        ]

        count = 0
        for entry in default_entries:
            self.create_knowledge(entry)
            count += 1
        return count

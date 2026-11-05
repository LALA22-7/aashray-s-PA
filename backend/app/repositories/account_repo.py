"""
Repository pattern for Account and PersonalityConfiguration persistence.
"""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.account import Account
from app.models.personality import PersonalityConfiguration


class AccountRepository:
    """Handles database queries and mutations for Account entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, account_id: str, load_personality: bool = True) -> Optional[Account]:
        """Retrieve an account by its unique UUID."""
        stmt = select(Account).where(Account.id == account_id)
        if load_personality:
            stmt = stmt.options(selectinload(Account.personality))
        return self.db.scalars(stmt).first()

    def get_by_platform_account_id(self, platform_account_id: str) -> Optional[Account]:
        """Retrieve an account by its external platform account ID."""
        stmt = (
            select(Account)
            .where(Account.platform_account_id == platform_account_id)
            .options(selectinload(Account.personality))
        )
        return self.db.scalars(stmt).first()

    def get_by_phone_number(self, phone_number: str) -> Optional[Account]:
        """Retrieve an account by its phone number."""
        stmt = (
            select(Account)
            .where(Account.phone_number == phone_number)
            .options(selectinload(Account.personality))
        )
        return self.db.scalars(stmt).first()

    def get_all(
        self,
        platform: Optional[str] = None,
        account_type: Optional[str] = None,
    ) -> Sequence[Account]:
        """Retrieve all accounts with optional filtering."""
        stmt = select(Account).options(selectinload(Account.personality)).order_by(Account.created_at)
        if platform:
            stmt = stmt.where(Account.platform == platform)
        if account_type:
            stmt = stmt.where(Account.account_type == account_type)
        return self.db.scalars(stmt).all()

    def create(self, account: Account) -> Account:
        """Persist a new account entity."""
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update(self, account: Account) -> Account:
        """Save modifications to an existing account entity."""
        self.db.commit()
        self.db.refresh(account)
        return account

    def delete(self, account: Account) -> None:
        """Delete an account entity and cascading relationships."""
        self.db.delete(account)
        self.db.commit()

    def get_personality(self, account_id: str) -> Optional[PersonalityConfiguration]:
        """Fetch personality configuration for a given account."""
        stmt = select(PersonalityConfiguration).where(
            PersonalityConfiguration.account_id == account_id
        )
        return self.db.scalars(stmt).first()

    def upsert_personality(
        self,
        account_id: str,
        personality: PersonalityConfiguration,
    ) -> PersonalityConfiguration:
        """Create or update personality configuration for an account."""
        existing = self.get_personality(account_id)
        if existing:
            # Update attributes
            for col in [
                "formality",
                "friendliness",
                "humour",
                "reply_length",
                "emoji_usage",
                "language_preference",
                "hinglish_preference",
                "common_expressions",
                "professionalism",
                "sales_orientation",
                "response_style",
                "system_prompt_override",
            ]:
                val = getattr(personality, col, None)
                if val is not None:
                    setattr(existing, col, val)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            personality.account_id = account_id
            self.db.add(personality)
            self.db.commit()
            self.db.refresh(personality)
            return personality

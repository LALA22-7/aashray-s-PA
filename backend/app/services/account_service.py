"""
Service layer for Account lifecycle, integration credential management,
and automation mode controls.
"""

from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.models.account import Account
from app.models.enums import (
    AccountType,
    AutomationMode,
    IntegrationStatus,
    IntegrationType,
    PlatformType,
    ReplyLength,
)
from app.models.personality import PersonalityConfiguration
from app.repositories.account_repo import AccountRepository
from app.schemas.account import (
    AccountConnectRequest,
    AccountCreate,
    AccountDetailRead,
    AccountRead,
    AccountUpdate,
)
from app.schemas.personality import PersonalityConfigRead, PersonalityConfigUpdate
from app.utils.encryption import decrypt_data, encrypt_data


# Global in-memory automation state (for instant emergency intervention)
_AUTOMATION_STATE = {
    "global_paused": False,
    "emergency_stopped": False,
}


class AccountService:
    """Orchestrates business operations on social communication accounts."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AccountRepository(db)

    # ── Account Lifecycle ──────────────────────────────────────────

    def create_account(self, data: AccountCreate) -> Account:
        """Create a new communication identity."""
        if data.platform_account_id:
            existing = self.repo.get_by_platform_account_id(data.platform_account_id)
            if existing:
                raise ConflictException(
                    f"Account with platform identifier '{data.platform_account_id}' already exists."
                )

        encrypted_creds = None
        integration_status = IntegrationStatus.DISCONNECTED
        if data.credentials:
            encrypted_creds = encrypt_data(data.credentials)
            integration_status = IntegrationStatus.CONNECTED

        account = Account(
            platform=data.platform.value,
            account_type=data.account_type.value,
            display_name=data.display_name,
            phone_number=data.phone_number,
            platform_account_id=data.platform_account_id,
            integration_type=data.integration_type.value,
            integration_status=integration_status.value,
            encrypted_credentials=encrypted_creds,
            automation_enabled=data.automation_enabled,
            automation_mode=data.automation_mode.value,
            language_preferences=data.language_preferences,
            context_window_size=data.context_window_size,
        )

        # Set up personality
        if data.personality:
            p = data.personality
            account.personality = PersonalityConfiguration(
                formality=p.formality,
                friendliness=p.friendliness,
                humour=p.humour,
                reply_length=p.reply_length.value,
                emoji_usage=p.emoji_usage,
                language_preference=p.language_preference,
                hinglish_preference=p.hinglish_preference,
                common_expressions=p.common_expressions,
                professionalism=p.professionalism,
                sales_orientation=p.sales_orientation,
                response_style=p.response_style,
                system_prompt_override=p.system_prompt_override,
            )
        else:
            # Generate default personality matching account type
            account.personality = self._build_default_personality(
                data.platform, data.account_type
            )

        return self.repo.create(account)

    def get_account_or_404(self, account_id: str) -> Account:
        """Retrieve an account by ID or raise NotFoundException."""
        account = self.repo.get_by_id(account_id)
        if not account:
            raise NotFoundException(f"Account with id '{account_id}' not found.")
        return account

    def list_accounts(
        self,
        platform: Optional[str] = None,
        account_type: Optional[str] = None,
    ) -> Sequence[Account]:
        """List all accounts with optional filters."""
        return self.repo.get_all(platform=platform, account_type=account_type)

    def update_account(self, account_id: str, data: AccountUpdate) -> Account:
        """Update account attributes."""
        account = self.get_account_or_404(account_id)

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(account, field) and value is not None:
                if hasattr(value, "value"):  # Enum support
                    setattr(account, field, value.value)
                else:
                    setattr(account, field, value)

        return self.repo.update(account)

    # ── Integration & Connection ───────────────────────────────────

    def connect_account(self, account_id: str, req: AccountConnectRequest) -> Account:
        """Store encrypted credentials and mark account connected."""
        account = self.get_account_or_404(account_id)

        account.encrypted_credentials = encrypt_data(req.credentials)
        if req.platform_account_id:
            account.platform_account_id = req.platform_account_id
        account.integration_status = IntegrationStatus.CONNECTED.value
        account.last_sync_at = datetime.now(timezone.utc)

        return self.repo.update(account)

    def disconnect_account(self, account_id: str) -> Account:
        """Revoke credentials and mark account disconnected."""
        account = self.get_account_or_404(account_id)

        account.encrypted_credentials = None
        account.integration_status = IntegrationStatus.DISCONNECTED.value
        account.automation_enabled = False

        return self.repo.update(account)

    def get_decrypted_credentials(self, account_id: str) -> str:
        """
        Internal method for integration adapters to retrieve credentials.
        Never exposed over the public API.
        """
        account = self.get_account_or_404(account_id)
        if not account.encrypted_credentials:
            return ""
        return decrypt_data(account.encrypted_credentials)

    # ── Personality Management ─────────────────────────────────────

    def get_personality(self, account_id: str) -> PersonalityConfiguration:
        """Get the personality configuration for an account."""
        account = self.get_account_or_404(account_id)
        if not account.personality:
            p = self._build_default_personality(
                PlatformType(account.platform), AccountType(account.account_type)
            )
            p.account_id = account.id
            account.personality = self.repo.upsert_personality(account.id, p)
        return account.personality

    def update_personality(
        self, account_id: str, data: PersonalityConfigUpdate
    ) -> PersonalityConfiguration:
        """Update tone and communication parameters for an account."""
        self.get_account_or_404(account_id)
        existing = self.get_personality(account_id)

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(existing, field) and value is not None:
                if hasattr(value, "value"):
                    setattr(existing, field, value.value)
                else:
                    setattr(existing, field, value)

        return self.repo.upsert_personality(account_id, existing)

    # ── Automation Controls ────────────────────────────────────────

    def set_account_automation(
        self,
        account_id: str,
        enabled: bool,
        mode: Optional[AutomationMode] = None,
    ) -> Account:
        """Configure automation on a single account."""
        account = self.get_account_or_404(account_id)
        account.automation_enabled = enabled
        if mode:
            account.automation_mode = mode.value
        return self.repo.update(account)

    @classmethod
    def pause_all_automation(cls) -> None:
        """Globally pause all outbound automations across all accounts."""
        _AUTOMATION_STATE["global_paused"] = True

    @classmethod
    def resume_all_automation(cls) -> None:
        """Resume global automation (unless emergency stopped)."""
        if _AUTOMATION_STATE["emergency_stopped"]:
            raise BadRequestException(
                "Cannot resume while Emergency Stop is active. Reset emergency stop first."
            )
        _AUTOMATION_STATE["global_paused"] = False

    @classmethod
    def emergency_stop(cls) -> None:
        """Emergency lock: immediate halt of all generation and delivery."""
        _AUTOMATION_STATE["emergency_stopped"] = True
        _AUTOMATION_STATE["global_paused"] = True

    @classmethod
    def reset_emergency_stop(cls) -> None:
        """Clear emergency stop flag."""
        _AUTOMATION_STATE["emergency_stopped"] = False

    @classmethod
    def get_global_automation_status(cls) -> dict:
        """Get the current global automation state flags."""
        return dict(_AUTOMATION_STATE)

    # ── Default Personality Builder ────────────────────────────────

    def _build_default_personality(
        self, platform: PlatformType, account_type: AccountType
    ) -> PersonalityConfiguration:
        """
        Creates an account-type-tailored personality configuration.
        """
        if account_type == AccountType.PERSONAL:
            # Casual, conversational, Hinglish-friendly, short
            return PersonalityConfiguration(
                formality=0.2,
                friendliness=0.85,
                humour=0.4,
                reply_length=ReplyLength.SHORT.value,
                emoji_usage=0.4,
                language_preference="hinglish",
                hinglish_preference=0.7,
                common_expressions=["Hey!", "Haan bilkul", "Sahi hai", "Done deal", "Pakka"],
                professionalism=0.2,
                sales_orientation=0.0,
                response_style="conversational",
                system_prompt_override=(
                    "You are replying as Aashray in a personal capacity. "
                    "Keep replies natural, casual, friendly, and brief. Use Hinglish where appropriate. "
                    "Never invent commitments or fabricate personal events."
                ),
            )
        else:
            # Business: Professional, customer-oriented, sales-aware, concise
            return PersonalityConfiguration(
                formality=0.7,
                friendliness=0.85,
                humour=0.1,
                reply_length=ReplyLength.SHORT.value,
                emoji_usage=0.2,
                language_preference="english",
                hinglish_preference=0.2,
                common_expressions=[
                    "Hi there!",
                    "Happy to help with bottle advertising enquiries.",
                    "Let us know your target location and campaign quantity.",
                ],
                professionalism=0.85,
                sales_orientation=0.75,
                response_style="consultative",
                system_prompt_override=(
                    "You are representing Aashray's Bottle Advertising Agency. "
                    "Respond professionally, concisely, and warmly. Explain advertising options, "
                    "qualify leads by asking for target campaign locations and quantities, "
                    "and never invent prices or unverified availability."
                ),
            )

    # ── Initial Four Accounts Seeder ───────────────────────────────

    def seed_default_accounts(self) -> list[Account]:
        """
        Ensures the four core accounts exist:
        1. Personal WhatsApp
        2. Business WhatsApp
        3. Personal Instagram
        4. Business Instagram
        """
        existing_accounts = self.repo.get_all()
        existing_keys = {
            (acc.platform, acc.account_type): acc for acc in existing_accounts
        }

        created = []

        # 1. Personal WhatsApp
        if (PlatformType.WHATSAPP.value, AccountType.PERSONAL.value) not in existing_keys:
            acc1 = self.create_account(
                AccountCreate(
                    platform=PlatformType.WHATSAPP,
                    account_type=AccountType.PERSONAL,
                    display_name="Aashray Personal WhatsApp",
                    phone_number="+91-PERSONAL",
                    integration_type=IntegrationType.MANUAL,
                    automation_enabled=False,
                    automation_mode=AutomationMode.APPROVAL,
                    context_window_size=12,
                )
            )
            created.append(acc1)

        # 2. Business WhatsApp
        if (PlatformType.WHATSAPP.value, AccountType.BUSINESS.value) not in existing_keys:
            acc2 = self.create_account(
                AccountCreate(
                    platform=PlatformType.WHATSAPP,
                    account_type=AccountType.BUSINESS,
                    display_name="Aashray Business WhatsApp",
                    phone_number="+91-BUSINESS",
                    integration_type=IntegrationType.WHATSAPP_CLOUD_API,
                    automation_enabled=True,
                    automation_mode=AutomationMode.AUTOMATIC,
                    context_window_size=15,
                )
            )
            created.append(acc2)

        # 3. Personal Instagram
        if (PlatformType.INSTAGRAM.value, AccountType.PERSONAL.value) not in existing_keys:
            acc3 = self.create_account(
                AccountCreate(
                    platform=PlatformType.INSTAGRAM,
                    account_type=AccountType.PERSONAL,
                    display_name="Aashray Personal Instagram",
                    integration_type=IntegrationType.MANUAL,
                    automation_enabled=False,
                    automation_mode=AutomationMode.APPROVAL,
                    context_window_size=10,
                )
            )
            created.append(acc3)

        # 4. Business Instagram
        if (PlatformType.INSTAGRAM.value, AccountType.BUSINESS.value) not in existing_keys:
            acc4 = self.create_account(
                AccountCreate(
                    platform=PlatformType.INSTAGRAM,
                    account_type=AccountType.BUSINESS,
                    display_name="Aashray Business Instagram",
                    integration_type=IntegrationType.INSTAGRAM_MESSAGING_API,
                    automation_enabled=True,
                    automation_mode=AutomationMode.AUTOMATIC,
                    context_window_size=15,
                )
            )
            created.append(acc4)

        return created

    # ── DTO Serialization Helpers ─────────────────────────────────

    @staticmethod
    def to_account_read(account: Account) -> AccountRead:
        """Convert ORM Account to AccountRead DTO."""
        return AccountRead(
            id=account.id,
            platform=PlatformType(account.platform),
            account_type=AccountType(account.account_type),
            display_name=account.display_name,
            phone_number=account.phone_number,
            platform_account_id=account.platform_account_id,
            integration_type=IntegrationType(account.integration_type),
            integration_status=IntegrationStatus(account.integration_status),
            automation_enabled=account.automation_enabled,
            automation_mode=AutomationMode(account.automation_mode),
            language_preferences=account.language_preferences,
            context_window_size=account.context_window_size,
            has_credentials=bool(account.encrypted_credentials),
            created_at=account.created_at,
            updated_at=account.updated_at,
            last_sync_at=account.last_sync_at,
        )

    @classmethod
    def to_account_detail_read(cls, account: Account) -> AccountDetailRead:
        """Convert ORM Account to AccountDetailRead DTO with personality."""
        read_dto = cls.to_account_read(account)
        personality_dto = None
        if account.personality:
            p = account.personality
            personality_dto = PersonalityConfigRead(
                id=p.id,
                account_id=p.account_id,
                formality=p.formality,
                friendliness=p.friendliness,
                humour=p.humour,
                reply_length=ReplyLength(p.reply_length),
                emoji_usage=p.emoji_usage,
                language_preference=p.language_preference,
                hinglish_preference=p.hinglish_preference,
                common_expressions=p.common_expressions,
                professionalism=p.professionalism,
                sales_orientation=p.sales_orientation,
                response_style=p.response_style,
                system_prompt_override=p.system_prompt_override,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )

        return AccountDetailRead(
            **read_dto.model_dump(),
            personality=personality_dto,
        )

"""
API endpoints for AI Reply Generation, Intent Testing, and Runtime Settings.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.engine import AIEngine
from app.ai.intent_classifier import IntentClassifier
from app.ai.personality import PersonalityEngine
from app.ai.providers import get_ai_provider
from app.ai.schemas import (
    AIResponsePayload,
    AISettingsRead,
    AISettingsUpdate,
    GenerateReplyRequest,
    IntentClassificationResult,
    TestMessageRequest,
    TestMessageResponse,
)
from app.api.deps import get_db
from app.config import get_settings
from app.models.enums import AccountType
from app.services.account_service import AccountService

router = APIRouter(prefix="/ai", tags=["AI Engine"])

# Runtime settings overrides
_RUNTIME_AI_SETTINGS = {
    "provider": None,
    "model": None,
    "temperature": 0.7,
}


@router.post("/generate-reply", response_model=AIResponsePayload)
def generate_reply(
    request: GenerateReplyRequest,
    db: Session = Depends(get_db),
) -> AIResponsePayload:
    """
    Generate an AI reply for an incoming message within an account context.
    Executes intent classification, persona assembly, generation, and safety checks.
    """
    account_service = AccountService(db)
    account = account_service.get_account_or_404(request.account_id)

    provider = get_ai_provider(
        provider_name=_RUNTIME_AI_SETTINGS["provider"],
        model=_RUNTIME_AI_SETTINGS["model"],
    )
    engine = AIEngine(provider=provider)
    return engine.process_message(account=account, request=request)


@router.post("/test-message", response_model=TestMessageResponse)
def test_message(
    request: TestMessageRequest,
    db: Session = Depends(get_db),
) -> TestMessageResponse:
    """
    Interactive test endpoint for the control dashboard to preview how
    the AI responds using an account's unique personality.
    """
    account_service = AccountService(db)
    account = account_service.get_account_or_404(request.account_id)

    provider = get_ai_provider(
        provider_name=_RUNTIME_AI_SETTINGS["provider"],
        model=_RUNTIME_AI_SETTINGS["model"],
    )
    engine = AIEngine(provider=provider)

    gen_req = GenerateReplyRequest(
        account_id=account.id,
        message=request.message,
        sender_name=request.sender_name,
        conversation_history=request.conversation_history,
    )

    result = engine.process_message(account=account, request=gen_req)

    system_prompt = PersonalityEngine.build_system_instruction(
        account=account, personality=account.personality
    )

    return TestMessageResponse(
        account_id=account.id,
        account_name=account.display_name,
        platform=account.platform,
        account_type=account.account_type,
        result=result,
        system_prompt_used=system_prompt,
    )


@router.post("/classify-intent", response_model=IntentClassificationResult)
def classify_intent(
    request: GenerateReplyRequest,
    db: Session = Depends(get_db),
) -> IntentClassificationResult:
    """
    Standalone intent classification endpoint for diagnostics.
    """
    account_service = AccountService(db)
    account = account_service.get_account_or_404(request.account_id)

    provider = get_ai_provider(
        provider_name=_RUNTIME_AI_SETTINGS["provider"],
        model=_RUNTIME_AI_SETTINGS["model"],
    )
    classifier = IntentClassifier(provider)

    return classifier.classify(
        message=request.message,
        account_type=AccountType(account.account_type),
        sender_name=request.sender_name,
    )


@router.get("/settings", response_model=AISettingsRead)
def get_ai_settings() -> AISettingsRead:
    """Inspect current active AI provider and model configurations."""
    settings = get_settings()
    active_provider = _RUNTIME_AI_SETTINGS["provider"] or settings.AI_PROVIDER
    active_model = _RUNTIME_AI_SETTINGS["model"] or settings.AI_MODEL

    return AISettingsRead(
        provider=active_provider,
        model=active_model,
        has_api_key=bool(settings.GEMINI_API_KEY),
        temperature=_RUNTIME_AI_SETTINGS["temperature"],
    )


@router.patch("/settings", response_model=AISettingsRead)
def update_ai_settings(data: AISettingsUpdate) -> AISettingsRead:
    """Dynamically modify the AI provider or model."""
    if data.provider is not None:
        _RUNTIME_AI_SETTINGS["provider"] = data.provider
    if data.model is not None:
        _RUNTIME_AI_SETTINGS["model"] = data.model
    if data.temperature is not None:
        _RUNTIME_AI_SETTINGS["temperature"] = data.temperature

    return get_ai_settings()

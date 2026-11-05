"""
Tests for AI provider abstraction and implementations.
"""

from pydantic import BaseModel

from app.ai.providers import (
    GeminiProvider,
    MockAIProvider,
    get_ai_provider,
)
from app.ai.schemas import AIResponsePayload, MessageIntent


class SimpleTestSchema(BaseModel):
    greeting: str
    number: int


def test_mock_provider_structured_generation() -> None:
    """MockAIProvider generates validated structured payloads."""
    provider = MockAIProvider()
    assert provider.is_healthy() is True

    result = provider.generate_structured(
        prompt="Hi, what are your bottle advertising rates?",
        system_instruction="You represent a business agency.",
        response_model=AIResponsePayload,
    )

    assert isinstance(result, AIResponsePayload)
    assert result.intent in (MessageIntent.PRICING_ENQUIRY, MessageIntent.BUSINESS_ENQUIRY)
    assert len(result.reply) > 10
    assert result.confidence > 0.8


def test_gemini_provider_health_check_without_key() -> None:
    """GeminiProvider is marked unhealthy when no API key is provided."""
    provider = GeminiProvider(api_key="")
    assert provider.is_healthy() is False


def test_provider_factory_fallback_to_mock() -> None:
    """When Gemini is selected without an API key, get_ai_provider falls back safely to MockAIProvider."""
    provider = get_ai_provider(provider_name="gemini", api_key="")
    assert isinstance(provider, MockAIProvider)
    assert provider.is_healthy() is True


def test_gemini_markdown_fence_cleaning() -> None:
    """Extract raw JSON text from markdown code fences."""
    fenced_text = "```json\n{\"intent\": \"greeting\", \"reply\": \"Hello!\"}\n```"
    cleaned = GeminiProvider._extract_json_from_text(fenced_text)
    assert cleaned == "{\"intent\": \"greeting\", \"reply\": \"Hello!\"}"

"""
AI Model providers package and factory constructor.
"""

import logging
from typing import Optional

from app.ai.providers.base import BaseAIProvider
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.mock import MockAIProvider
from app.config import get_settings

logger = logging.getLogger("aashrayspa.ai.providers")


def get_ai_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> BaseAIProvider:
    """
    Factory function to retrieve the configured AI provider instance.
    If provider is 'gemini' but no API key is provided, falls back to MockAIProvider
    with an advisory log.
    """
    settings = get_settings()
    selected_provider = (provider_name or settings.AI_PROVIDER).lower()

    if selected_provider == "gemini":
        gemini = GeminiProvider(api_key=api_key, model=model)
        if gemini.is_healthy():
            return gemini
        logger.warning(
            "Gemini provider selected but GEMINI_API_KEY is not configured. Falling back to MockAIProvider."
        )
        return MockAIProvider()

    if selected_provider == "mock":
        return MockAIProvider()

    raise ValueError(f"Unsupported AI provider: '{selected_provider}'")


__all__ = ["BaseAIProvider", "GeminiProvider", "MockAIProvider", "get_ai_provider"]

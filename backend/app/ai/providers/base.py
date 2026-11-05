"""
Abstract base class for AI Model providers.
"""

from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseAIProvider(ABC):
    """Abstract interface that all LLM providers (Gemini, Mock, etc.) must implement."""

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_model: Type[T],
        temperature: float = 0.7,
    ) -> T:
        """
        Generate a strictly validated Pydantic model response from the LLM.
        """
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate freeform text from the LLM.
        """
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check provider connectivity and configuration status."""
        pass


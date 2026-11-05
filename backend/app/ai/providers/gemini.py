"""
Google Gemini API integration provider utilizing the REST endpoint and HTTPX.
"""

import json
import logging
import re
from typing import Any, Optional, Type, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.ai.providers.base import BaseAIProvider
from app.config import get_settings
from app.core.exceptions import IntegrationException

logger = logging.getLogger("aashrayspa.ai.gemini")
T = TypeVar("T", bound=BaseModel)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(BaseAIProvider):
    """
    Calls the Google Gemini API (default model: gemini-2.0-flash)
    using HTTPX with structured JSON outputs.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.AI_MODEL
        self.timeout = timeout

    def is_healthy(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate freeform text using Gemini API."""
        if not self.is_healthy():
            raise IntegrationException("Gemini API key is not configured.")

        url = f"{GEMINI_BASE_URL}/models/{self.model}:generateContent?key={self.api_key}"

        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        data = self._execute_request(url, payload)
        try:
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            return ""
        except Exception as exc:
            logger.error("Failed to parse Gemini text response", exc_info=exc)
            raise IntegrationException(f"Error parsing Gemini response: {exc}")

    def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_model: Type[T],
        temperature: float = 0.7,
    ) -> T:
        """
        Generate and validate a structured Pydantic response from Gemini.
        Uses responseMimeType='application/json' and JSON Schema enforcement.
        """
        if not self.is_healthy():
            raise IntegrationException("Gemini API key is not configured.")

        url = f"{GEMINI_BASE_URL}/models/{self.model}:generateContent?key={self.api_key}"

        # Extract JSON schema from Pydantic model
        schema = response_model.model_json_schema()
        clean_schema = self._clean_json_schema_for_gemini(schema)

        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
                "responseSchema": clean_schema,
            },
        }

        data = self._execute_request(url, payload)
        raw_text = ""
        try:
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    raw_text = parts[0].get("text", "")

            cleaned_json = self._extract_json_from_text(raw_text)
            parsed_dict = json.loads(cleaned_json)
            return response_model.model_validate(parsed_dict)
        except ValidationError as val_err:
            logger.error(f"Gemini output validation error against {response_model.__name__}: {val_err}. Raw text: {raw_text}")
            raise IntegrationException(
                f"Gemini returned an invalid data structure: {val_err.errors()}"
            )
        except json.JSONDecodeError as decode_err:
            logger.error(f"Gemini output could not be decoded as JSON: {decode_err}. Raw: {raw_text}")
            raise IntegrationException(f"Gemini output was not valid JSON: {decode_err}")

    def _execute_request(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute HTTP POST with error wrapping."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
                if resp.status_code != 200:
                    logger.error(
                        "Gemini API returned non-200 status",
                        extra={"status_code": resp.status_code, "body": resp.text},
                    )
                    raise IntegrationException(
                        f"Gemini API error (HTTP {resp.status_code}): {resp.text}"
                    )
                return resp.json()
        except httpx.TimeoutException:
            logger.error("Gemini API request timed out")
            raise IntegrationException("AI provider request timed out.")
        except httpx.RequestError as req_err:
            logger.error(f"Gemini network request error: {req_err}")
            raise IntegrationException(f"Network error connecting to AI provider: {req_err}")

    @staticmethod
    def _extract_json_from_text(text: str) -> str:
        """Strip markdown code fence blocks if returned by the LLM."""
        text = text.strip()
        # Look for ```json ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            return fence_match.group(1).strip()
        return text

    @staticmethod
    def _clean_json_schema_for_gemini(schema: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize standard Pydantic JSON schema to Gemini-supported JSON schema subset
        (removes titles, definitions that can confuse the Gemini engine).
        """
        cleaned = dict(schema)
        cleaned.pop("$defs", None)
        cleaned.pop("definitions", None)
        cleaned.pop("title", None)
        return cleaned

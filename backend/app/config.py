"""
Application configuration using pydantic-settings.

All settings are loaded from environment variables or a .env file.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "AashraysPA"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-change-in-production"

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./aashrays_pa.db"

    # ── AI Provider ──────────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    AI_PROVIDER: str = "gemini"
    AI_MODEL: str = "gemini-2.0-flash"

    # ── Security / JWT ───────────────────────────────────────────
    JWT_SECRET_KEY: str = "dev-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440
    ENCRYPTION_KEY: str = ""

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── WhatsApp Cloud API ───────────────────────────────────────
    WHATSAPP_API_VERSION: str = "v21.0"
    WHATSAPP_VERIFY_TOKEN: str = "aashrays_pa_wa_verify_token"
    WHATSAPP_BUSINESS_PHONE_ID: str = ""
    WHATSAPP_BUSINESS_ACCESS_TOKEN: str = ""

    # ── WhatsApp Personal Bridge (Multi-Device Companion) ────────
    WHATSAPP_PERSONAL_BRIDGE_URL: str = "http://localhost:3001"

    # ── Instagram API ────────────────────────────────────────────
    INSTAGRAM_API_VERSION: str = "v21.0"
    INSTAGRAM_VERIFY_TOKEN: str = "aashrays_pa_ig_verify_token"
    INSTAGRAM_APP_ID: str = ""
    INSTAGRAM_APP_SECRET: str = ""
    INSTAGRAM_ACCESS_TOKEN: str = ""

    # ── Logging ──────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings (singleton)."""
    return Settings()


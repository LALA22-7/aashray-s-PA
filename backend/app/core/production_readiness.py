"""
Production readiness validation logic.
Ensures critical security settings, credentials, and databases are strictly validated
before running in production environments.
"""

import base64
import logging
from typing import NamedTuple

from app.config import Settings

logger = logging.getLogger("aashrayspa.production_readiness")


class ValidationIssue(NamedTuple):
    level: str  # "ERROR" | "WARNING"
    field: str
    message: str


def validate_production_configuration(settings: Settings) -> list[ValidationIssue]:
    """
    Validates settings for production environments.
    Returns a list of validation issues (ERRORs block startup, WARNINGs alert operator).
    """
    issues: list[ValidationIssue] = []

    is_prod = settings.APP_ENV.lower() in ("production", "prod")

    if not is_prod:
        return issues

    # 1. Database Backend Check
    if "sqlite" in settings.DATABASE_URL.lower():
        issues.append(
            ValidationIssue(
                level="ERROR",
                field="DATABASE_URL",
                message="SQLite is not supported in production. Use PostgreSQL (e.g., Supabase or Render Postgres).",
            )
        )

    # 2. Secret Key Check
    if settings.SECRET_KEY in ("dev-secret-change-in-production", "", "change-me"):
        issues.append(
            ValidationIssue(
                level="ERROR",
                field="SECRET_KEY",
                message="SECRET_KEY is using an insecure default. Generate a strong 32+ character random string.",
            )
        )

    # 3. JWT Secret Key Check
    if settings.JWT_SECRET_KEY in ("dev-jwt-secret-change-in-production", "", "change-me"):
        issues.append(
            ValidationIssue(
                level="ERROR",
                field="JWT_SECRET_KEY",
                message="JWT_SECRET_KEY is using an insecure default. Generate a dedicated secret key.",
            )
        )

    # 4. Credential Encryption Key (Fernet) Check
    if not settings.ENCRYPTION_KEY:
        issues.append(
            ValidationIssue(
                level="ERROR",
                field="ENCRYPTION_KEY",
                message="ENCRYPTION_KEY is required in production to protect integration tokens.",
            )
        )
    else:
        try:
            decoded = base64.urlsafe_b64decode(settings.ENCRYPTION_KEY)
            if len(decoded) != 32:
                issues.append(
                    ValidationIssue(
                        level="ERROR",
                        field="ENCRYPTION_KEY",
                        message="ENCRYPTION_KEY must be a valid 32-byte urlsafe base64-encoded string.",
                    )
                )
        except Exception:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    field="ENCRYPTION_KEY",
                    message="ENCRYPTION_KEY is not a valid base64-encoded Fernet key.",
                )
            )

    # 5. Debug Mode Check
    if settings.DEBUG:
        issues.append(
            ValidationIssue(
                level="WARNING",
                field="DEBUG",
                message="DEBUG mode is enabled. Set DEBUG=false in production to prevent stack trace leakage.",
            )
        )

    # 6. AI Provider Check
    if not settings.GEMINI_API_KEY and settings.AI_PROVIDER == "gemini":
        issues.append(
            ValidationIssue(
                level="WARNING",
                field="GEMINI_API_KEY",
                message="GEMINI_API_KEY is not set. The system will fall back to MockAIProvider.",
            )
        )

    # 7. WhatsApp Credentials Warning
    if not settings.WHATSAPP_BUSINESS_ACCESS_TOKEN or not settings.WHATSAPP_BUSINESS_PHONE_ID:
        issues.append(
            ValidationIssue(
                level="WARNING",
                field="WHATSAPP_BUSINESS_*",
                message="WhatsApp Business credentials are not configured. WhatsApp outbound will operate in simulated mode.",
            )
        )

    # 8. Instagram Credentials Warning
    if not settings.INSTAGRAM_ACCESS_TOKEN:
        issues.append(
            ValidationIssue(
                level="WARNING",
                field="INSTAGRAM_ACCESS_TOKEN",
                message="Instagram access token is not configured. Instagram outbound will operate in simulated mode.",
            )
        )

    return issues


def assert_production_ready(settings: Settings) -> None:
    """
    Evaluates configuration and raises a RuntimeError if any ERROR level issues exist.
    Logs WARNING level issues.
    """
    issues = validate_production_configuration(settings)
    errors = [i for i in issues if i.level == "ERROR"]
    warnings = [i for i in issues if i.level == "WARNING"]

    for w in warnings:
        logger.warning(f"[PRODUCTION READINESS WARNING] {w.field}: {w.message}")

    if errors:
        for e in errors:
            logger.critical(f"[PRODUCTION READINESS ERROR] {e.field}: {e.message}")
        error_details = "\n".join(f"- {e.field}: {e.message}" for e in errors)
        raise RuntimeError(
            f"Production configuration validation failed with {len(errors)} critical error(s):\n{error_details}"
        )

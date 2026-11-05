"""
Tests for production readiness validation, security constraints, and deployment integrity.
"""

import pytest
from cryptography.fernet import Fernet

from app.config import Settings
from app.core.production_readiness import (
    assert_production_ready,
    validate_production_configuration,
)


def test_dev_environment_skips_production_checks() -> None:
    """In development mode, default dev keys and SQLite are allowed."""
    dev_settings = Settings(
        APP_ENV="development",
        DATABASE_URL="sqlite:///./dev.db",
        SECRET_KEY="dev-secret-change-in-production",
        JWT_SECRET_KEY="dev-jwt-secret-change-in-production",
        ENCRYPTION_KEY="",
        DEBUG=True,
    )
    issues = validate_production_configuration(dev_settings)
    assert len(issues) == 0


def test_production_catches_sqlite_database() -> None:
    """In production mode, SQLite must be rejected with an ERROR."""
    prod_settings = Settings(
        APP_ENV="production",
        DATABASE_URL="sqlite:///./prod.db",
        SECRET_KEY="a" * 32,
        JWT_SECRET_KEY="b" * 32,
        ENCRYPTION_KEY=Fernet.generate_key().decode(),
        DEBUG=False,
    )
    issues = validate_production_configuration(prod_settings)
    errors = [i for i in issues if i.level == "ERROR"]
    assert any(e.field == "DATABASE_URL" for e in errors)


def test_production_catches_default_secrets() -> None:
    """In production mode, default dev secrets must be flagged as critical errors."""
    prod_settings = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql://user:pass@localhost:5432/db",
        SECRET_KEY="dev-secret-change-in-production",
        JWT_SECRET_KEY="dev-jwt-secret-change-in-production",
        ENCRYPTION_KEY="",
        DEBUG=False,
    )
    issues = validate_production_configuration(prod_settings)
    errors = [i for i in issues if i.level == "ERROR"]

    field_names = [e.field for e in errors]
    assert "SECRET_KEY" in field_names
    assert "JWT_SECRET_KEY" in field_names
    assert "ENCRYPTION_KEY" in field_names


def test_production_catches_invalid_fernet_encryption_key() -> None:
    """In production mode, invalid Fernet encryption keys are rejected."""
    prod_settings = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql://user:pass@localhost:5432/db",
        SECRET_KEY="a" * 32,
        JWT_SECRET_KEY="b" * 32,
        ENCRYPTION_KEY="invalid-non-base64-key",
        DEBUG=False,
    )
    issues = validate_production_configuration(prod_settings)
    errors = [i for i in issues if i.level == "ERROR"]
    assert any(e.field == "ENCRYPTION_KEY" for e in errors)


def test_production_valid_configuration_passes() -> None:
    """A properly configured production environment passes with zero errors."""
    valid_key = Fernet.generate_key().decode()
    prod_settings = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql://user:pass@localhost:5432/prod_db",
        SECRET_KEY="secure_production_secret_key_at_least_32_characters",
        JWT_SECRET_KEY="secure_production_jwt_key_at_least_32_characters",
        ENCRYPTION_KEY=valid_key,
        DEBUG=False,
    )
    issues = validate_production_configuration(prod_settings)
    errors = [i for i in issues if i.level == "ERROR"]
    assert len(errors) == 0

    # assert_production_ready should complete cleanly without throwing
    assert_production_ready(prod_settings)


def test_assert_production_ready_raises_runtime_error_on_insecure_defaults() -> None:
    """assert_production_ready raises RuntimeError when critical errors exist."""
    bad_settings = Settings(
        APP_ENV="production",
        DATABASE_URL="sqlite:///./test.db",
        SECRET_KEY="dev-secret-change-in-production",
    )
    with pytest.raises(RuntimeError) as exc_info:
        assert_production_ready(bad_settings)
    assert "Production configuration validation failed" in str(exc_info.value)

"""Tests for application configuration / settings."""

from app.config import Settings, get_settings


def test_settings_defaults() -> None:
    """Verify that default settings values are correct."""
    s = Settings()
    assert s.APP_NAME == "AashraysPA"
    assert s.APP_VERSION == "0.1.0"
    assert s.APP_ENV == "development"
    assert s.DEBUG is True
    assert "sqlite" in s.DATABASE_URL


def test_settings_app_name() -> None:
    """Check APP_NAME default is 'AashraysPA'."""
    s = Settings()
    assert s.APP_NAME == "AashraysPA"


def test_get_settings_returns_singleton() -> None:
    """get_settings() returns a cached instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2

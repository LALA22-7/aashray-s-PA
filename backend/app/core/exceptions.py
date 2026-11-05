"""
Custom exception classes for the application.
"""

from typing import Any


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        detail: str = "An error occurred",
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        self.extra = extra or {}
        super().__init__(self.detail)


class NotFoundException(AppException):
    """Resource not found (404)."""

    def __init__(self, detail: str = "Resource not found", **kwargs: Any) -> None:
        super().__init__(detail=detail, status_code=404, error_code="NOT_FOUND", **kwargs)


class BadRequestException(AppException):
    """Bad request (400)."""

    def __init__(self, detail: str = "Bad request", **kwargs: Any) -> None:
        super().__init__(detail=detail, status_code=400, error_code="BAD_REQUEST", **kwargs)


class UnauthorizedException(AppException):
    """Unauthorized (401)."""

    def __init__(self, detail: str = "Unauthorized", **kwargs: Any) -> None:
        super().__init__(detail=detail, status_code=401, error_code="UNAUTHORIZED", **kwargs)


class ForbiddenException(AppException):
    """Forbidden (403)."""

    def __init__(self, detail: str = "Forbidden", **kwargs: Any) -> None:
        super().__init__(detail=detail, status_code=403, error_code="FORBIDDEN", **kwargs)


class ConflictException(AppException):
    """Conflict (409)."""

    def __init__(self, detail: str = "Conflict", **kwargs: Any) -> None:
        super().__init__(detail=detail, status_code=409, error_code="CONFLICT", **kwargs)


class IntegrationException(AppException):
    """External integration failure (502)."""

    def __init__(self, detail: str = "Integration error", **kwargs: Any) -> None:
        super().__init__(detail=detail, status_code=502, error_code="INTEGRATION_ERROR", **kwargs)


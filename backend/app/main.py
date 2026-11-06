"""
Aashray'sPA — FastAPI application entry point.

One AI Brain. Four Account Identities. One Control Dashboard.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from app.api.router import api_router, api_v1_router
from app.api.v1.webhooks import router as webhooks_router
from app.config import get_settings
from app.core.exceptions import AppException
from app.core.middleware import setup_middleware
from app.core.production_readiness import assert_production_ready
from app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle."""
    settings = get_settings()
    app_logger = setup_logging(settings.LOG_LEVEL)
    app_logger.info(
        f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting "
        f"(env={settings.APP_ENV})"
    )
    # Validate production configuration if running in production mode
    assert_production_ready(settings)
    yield
    app_logger.info(f"👋 {settings.APP_NAME} shutting down")


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "AI-powered personal and business communication assistant. "
            "One AI Brain. Four Account Identities. One Control Dashboard."
        ),
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── Middleware ────────────────────────────────────────────────
    setup_middleware(app)

    # ── Routes ───────────────────────────────────────────────────
    # Support both /api and /api/v1 prefixes for robust client compatibility
    app.include_router(api_router)
    app.include_router(api_v1_router)

    # Webhooks available at /webhooks and versioned aliases
    app.include_router(webhooks_router)
    app.include_router(webhooks_router, prefix="/api")
    app.include_router(webhooks_router, prefix="/api/v1")

    # ── Root & Convenience endpoints ─────────────────────────────
    @app.get("/", tags=["Root"])
    def root() -> dict:
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/api/health",
        }

    @app.get("/health", tags=["Health"])
    def direct_health() -> dict:
        from datetime import datetime, timezone
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        return Response(status_code=204)

    # ── Exception handlers ───────────────────────────────────────
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "detail": exc.detail,
                "extra": exc.extra,
            },
        )

    return app


app = create_app()


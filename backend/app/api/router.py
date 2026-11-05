"""
Master API router aggregating all versioned sub-routers.
"""

from fastapi import APIRouter

from app.api.v1.accounts import router as accounts_router
from app.api.v1.automation import router as automation_router
from app.api.v1.health import router as health_router

api_router = APIRouter(prefix="/api")

# ── v1 routes ────────────────────────────────────────────────────
api_router.include_router(health_router)
api_router.include_router(accounts_router)
api_router.include_router(automation_router)


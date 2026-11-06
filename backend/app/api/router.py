"""
Master API router aggregating all versioned sub-routers.
"""

from fastapi import APIRouter

from app.api.v1.accounts import router as accounts_router
from app.api.v1.ai import router as ai_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.automation import router as automation_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.health import router as health_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.safety import router as safety_router

# ── Versioned Core Router ───────────────────────────────────────
v1_router = APIRouter()
v1_router.include_router(health_router)
v1_router.include_router(analytics_router)
v1_router.include_router(accounts_router)
v1_router.include_router(automation_router)
v1_router.include_router(ai_router)
v1_router.include_router(conversations_router)
v1_router.include_router(knowledge_router)
v1_router.include_router(safety_router)

# Provide both /api and /api/v1 for seamless compatibility
api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(v1_router)


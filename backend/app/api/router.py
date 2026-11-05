"""
Master API router aggregating all versioned sub-routers.
"""

from fastapi import APIRouter

from app.api.v1.accounts import router as accounts_router
from app.api.v1.ai import router as ai_router
from app.api.v1.automation import router as automation_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.health import router as health_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.safety import router as safety_router

api_router = APIRouter(prefix="/api")

# ── v1 routes ────────────────────────────────────────────────────
api_router.include_router(health_router)
api_router.include_router(accounts_router)
api_router.include_router(automation_router)
api_router.include_router(ai_router)
api_router.include_router(conversations_router)
api_router.include_router(knowledge_router)
api_router.include_router(safety_router)


"""
FastAPI dependency injection functions.
"""

# Re-export get_db directly so overrides in tests work on the same function object
from app.database.session import get_db  # noqa: F401


# TODO: Phase 2+ – implement proper authentication
async def get_current_user() -> dict:
    """
    Placeholder for authenticated user dependency.
    Will be replaced with JWT-based auth in a later phase.
    """
    return {"id": "owner", "role": "admin"}

"""
API endpoints for system-wide automation controls, pause/resume, and emergency intervention.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import AutomationMode
from app.schemas.automation import AutomationGlobalSettings
from app.services.account_service import AccountService

router = APIRouter(prefix="/automation", tags=["Automation"])


@router.get("/settings", response_model=AutomationGlobalSettings)
def get_automation_settings(db: Session = Depends(get_db)) -> AutomationGlobalSettings:
    """Get system-wide automation status and account mode counts."""
    service = AccountService(db)
    accounts = service.list_accounts()
    status_flags = AccountService.get_global_automation_status()

    auto_count = sum(1 for a in accounts if a.automation_mode == AutomationMode.AUTOMATIC.value and a.automation_enabled)
    approval_count = sum(1 for a in accounts if a.automation_mode == AutomationMode.APPROVAL.value and a.automation_enabled)
    disabled_count = sum(1 for a in accounts if not a.automation_enabled or a.automation_mode == AutomationMode.DISABLED.value)

    return AutomationGlobalSettings(
        global_paused=status_flags["global_paused"],
        emergency_stopped=status_flags["emergency_stopped"],
        active_accounts_count=len([a for a in accounts if a.automation_enabled]),
        automatic_mode_accounts_count=auto_count,
        approval_mode_accounts_count=approval_count,
        disabled_mode_accounts_count=disabled_count,
    )


@router.post("/pause")
def pause_automation() -> dict:
    """Globally suspend automatic response generation and delivery across all accounts."""
    AccountService.pause_all_automation()
    return {"status": "paused", "message": "All automations globally paused."}


@router.post("/resume")
def resume_automation() -> dict:
    """Resume global automation operations."""
    AccountService.resume_all_automation()
    return {"status": "active", "message": "Global automations resumed."}


@router.post("/emergency-stop")
def emergency_stop() -> dict:
    """
    Emergency intervention: immediately lock down all outbound messaging and AI generation.
    Requires explicit reset to clear.
    """
    AccountService.emergency_stop()
    return {
        "status": "emergency_stopped",
        "message": "Emergency Stop activated. Outbound messaging completely locked.",
    }


@router.post("/reset-emergency-stop")
def reset_emergency_stop() -> dict:
    """Clear emergency stop lock (automations remain paused until explicitly resumed)."""
    AccountService.reset_emergency_stop()
    return {
        "status": "emergency_cleared",
        "message": "Emergency stop cleared. Global automation is paused; invoke /resume when ready.",
    }

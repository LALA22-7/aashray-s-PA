"""
Automated tests for Phase 5: Safety Policy, Emergency Interventions, Deduplication, and Lead Capture.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.ai.schemas import AIResponsePayload, ConversationMode, MessageIntent
from app.schemas.safety import PolicyAction
from app.services.safety_service import SafetyService


def test_policy_evaluation_disabled_mode(client: TestClient, db_session: Session) -> None:
    """When account mode is DISABLED, policy forbids automatic sending."""
    seed_resp = client.post("/api/accounts/seed")
    acc_id = seed_resp.json()[0]["id"]

    # Set mode to disabled
    client.patch(f"/api/accounts/{acc_id}", json={"automation_enabled": True, "automation_mode": "disabled"})

    safety = SafetyService(db_session)
    account = safety.account_repo.get_by_id(acc_id)
    assert account is not None

    ai_resp = AIResponsePayload(
        intent=MessageIntent.GREETING,
        mode=ConversationMode.PERSONAL,
        reply="Hello!",
        confidence=0.95,
        requires_human=False,
    )

    decision = safety.evaluate_outbound_policy(account, ai_resp)
    assert decision.action == PolicyAction.DO_NOT_SEND
    assert decision.is_authorized is False


def test_policy_evaluation_approval_mode(client: TestClient, db_session: Session) -> None:
    """When account mode is APPROVAL, policy queues for human review."""
    seed_resp = client.post("/api/accounts/seed")
    acc_id = seed_resp.json()[0]["id"]

    client.patch(f"/api/accounts/{acc_id}", json={"automation_enabled": True, "automation_mode": "approval"})

    safety = SafetyService(db_session)
    account = safety.account_repo.get_by_id(acc_id)
    assert account is not None

    ai_resp = AIResponsePayload(
        intent=MessageIntent.GREETING,
        mode=ConversationMode.PERSONAL,
        reply="Hey there!",
        confidence=0.92,
        requires_human=False,
    )

    decision = safety.evaluate_outbound_policy(account, ai_resp)
    assert decision.action == PolicyAction.QUEUE_FOR_APPROVAL
    assert decision.is_authorized is False


def test_policy_evaluation_automatic_mode_authorized(client: TestClient, db_session: Session) -> None:
    """When account mode is AUTOMATIC with high confidence, outbound is authorized."""
    seed_resp = client.post("/api/accounts/seed")
    biz_wa = next(a for a in seed_resp.json() if a["platform"] == "whatsapp" and a["account_type"] == "business")

    client.patch(f"/api/accounts/{biz_wa['id']}", json={"automation_enabled": True, "automation_mode": "automatic"})

    safety = SafetyService(db_session)
    account = safety.account_repo.get_by_id(biz_wa["id"])
    assert account is not None

    ai_resp = AIResponsePayload(
        intent=MessageIntent.GREETING,
        mode=ConversationMode.BUSINESS,
        reply="Welcome to Aashray's Bottle Advertising Agency!",
        confidence=0.95,
        requires_human=False,
    )

    decision = safety.evaluate_outbound_policy(account, ai_resp)
    assert decision.action == PolicyAction.SEND_AUTOMATIC
    assert decision.is_authorized is True


def test_policy_evaluation_escalates_sensitive_intent(client: TestClient, db_session: Session) -> None:
    """Complaints and negotiations in AUTOMATIC mode are escalated to human review."""
    seed_resp = client.post("/api/accounts/seed")
    biz_wa = next(a for a in seed_resp.json() if a["platform"] == "whatsapp" and a["account_type"] == "business")

    safety = SafetyService(db_session)
    account = safety.account_repo.get_by_id(biz_wa["id"])
    assert account is not None

    ai_resp = AIResponsePayload(
        intent=MessageIntent.COMPLAINT,
        mode=ConversationMode.BUSINESS,
        reply="Sorry about the issue, let me escalate.",
        confidence=0.90,
        requires_human=True,
        reason="Customer complaint reported",
    )

    decision = safety.evaluate_outbound_policy(account, ai_resp)
    assert decision.action == PolicyAction.ESCALATE
    assert decision.is_authorized is False
    assert decision.requires_human is True


def test_policy_evaluation_emergency_stop_overrides_everything(client: TestClient, db_session: Session) -> None:
    """Emergency Stop forces DO_NOT_SEND across all accounts regardless of settings."""
    seed_resp = client.post("/api/accounts/seed")
    acc_id = seed_resp.json()[0]["id"]

    # Trigger emergency stop
    client.post("/api/automation/emergency-stop")

    try:
        safety = SafetyService(db_session)
        account = safety.account_repo.get_by_id(acc_id)
        assert account is not None

        ai_resp = AIResponsePayload(
            intent=MessageIntent.GREETING,
            mode=ConversationMode.PERSONAL,
            reply="Hello",
            confidence=0.99,
            requires_human=False,
        )

        decision = safety.evaluate_outbound_policy(account, ai_resp)
        assert decision.action == PolicyAction.DO_NOT_SEND
        assert decision.is_authorized is False
    finally:
        # Reset emergency stop for subsequent tests
        client.post("/api/automation/reset-emergency-stop")
        client.post("/api/automation/resume")


def test_webhook_event_deduplication(db_session: Session) -> None:
    """Detects duplicate platform event IDs for idempotent webhook processing."""
    safety = SafetyService(db_session)
    event_id = "meta-wamid-unique-event-12345"

    # Initially not duplicate
    assert safety.is_duplicate_webhook(event_id) is False

    # Record event
    safety.webhook_repo.record_event(
        platform="whatsapp",
        event_type="message",
        platform_event_id=event_id,
        raw_payload={"id": event_id, "text": "hello"},
    )

    # Now must be duplicate
    assert safety.is_duplicate_webhook(event_id) is True


def test_automated_lead_capture_and_update(client: TestClient, db_session: Session) -> None:
    """Captures lead from business enquiry and allows status update via API."""
    seed_resp = client.post("/api/accounts/seed")
    biz_wa = next(a for a in seed_resp.json() if a["platform"] == "whatsapp" and a["account_type"] == "business")

    # Create through manual-input endpoint on business account
    manual_resp = client.post(
        "/api/conversations/manual-input",
        json={
            "account_id": biz_wa["id"],
            "sender_contact_id": "+91-9988776655",
            "sender_name": "Karan Singhania",
            "message_content": "We need 5,000 promotional water bottles for a marathon in Delhi.",
            "record_in_history": True,
        },
    )
    assert manual_resp.status_code == 200
    conv_id = manual_resp.json()["conversation_id"]
    contact_id = manual_resp.json()["contact_id"]

    safety = SafetyService(db_session)
    account = safety.account_repo.get_by_id(biz_wa["id"])
    assert account is not None

    ai_payload = AIResponsePayload(
        intent=MessageIntent.BUSINESS_ENQUIRY,
        mode=ConversationMode.BUSINESS,
        reply="Hey Karan! We can certainly manage 5,000 bottles in Delhi.",
        confidence=0.94,
        extracted_lead_info={"quantity": 5000, "location": "Delhi"},
    )

    captured_lead = safety.capture_lead_if_qualified(
        account=account,
        conversation_id=conv_id,
        contact_id=contact_id,
        ai_response=ai_payload,
        customer_name="Karan Singhania",
        incoming_message="5,000 bottles marathon",
    )
    assert captured_lead is not None
    assert captured_lead.estimated_quantity == 5000
    assert captured_lead.location == "Delhi"
    lead_id = captured_lead.id

    # Query leads endpoint
    leads_resp = client.get("/api/leads")
    assert leads_resp.status_code == 200
    leads = leads_resp.json()
    assert any(lead_item["id"] == lead_id for lead_item in leads)

    # Patch lead status to qualified
    patch_resp = client.patch(f"/api/leads/{lead_id}", json={"status": "qualified", "follow_up_notes": "Sent rate card."})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "qualified"
    assert patch_resp.json()["follow_up_notes"] == "Sent rate card."


def test_audit_logs_retrieval(client: TestClient) -> None:
    """GET /api/audit-logs retrieves recorded system audit entries."""
    logs_resp = client.get("/api/audit-logs")
    assert logs_resp.status_code == 200
    assert isinstance(logs_resp.json(), list)

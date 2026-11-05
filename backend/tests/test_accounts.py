"""
Automated tests for Phase 2: Account Management & Automation Controls.
"""

from fastapi.testclient import TestClient


def test_seed_default_accounts(client: TestClient) -> None:
    """POST /api/accounts/seed initializes the 4 foundational accounts."""
    response = client.post("/api/accounts/seed")
    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) == 4

    # Verify each required identity is present
    platforms = {(a["platform"], a["account_type"]) for a in accounts}
    assert ("whatsapp", "personal") in platforms
    assert ("whatsapp", "business") in platforms
    assert ("instagram", "personal") in platforms
    assert ("instagram", "business") in platforms

    # Verify WhatsApp accounts have their respective phone numbers configured
    wa_personal = next(a for a in accounts if a["platform"] == "whatsapp" and a["account_type"] == "personal")
    wa_business = next(a for a in accounts if a["platform"] == "whatsapp" and a["account_type"] == "business")
    assert wa_personal["phone_number"] == "+91-PERSONAL"
    assert wa_business["phone_number"] == "+91-BUSINESS"

    # Verify seeding is idempotent (calling it again returns the same 4 accounts without duplicates)
    response_second = client.post("/api/accounts/seed")
    assert response_second.status_code == 200
    assert len(response_second.json()) == 4


def test_list_accounts_with_filters(client: TestClient) -> None:
    """GET /api/accounts supports filtering by platform and account_type."""
    client.post("/api/accounts/seed")

    # Filter by platform
    wa_resp = client.get("/api/accounts?platform=whatsapp")
    assert wa_resp.status_code == 200
    assert len(wa_resp.json()) == 2
    assert all(a["platform"] == "whatsapp" for a in wa_resp.json())

    # Filter by account_type
    biz_resp = client.get("/api/accounts?account_type=business")
    assert biz_resp.status_code == 200
    assert len(biz_resp.json()) == 2
    assert all(a["account_type"] == "business" for a in biz_resp.json())


def test_get_account_detail_includes_personality(client: TestClient) -> None:
    """GET /api/accounts/{id} includes the tailored personality profile."""
    seed_resp = client.post("/api/accounts/seed")
    account_id = seed_resp.json()[0]["id"]

    detail_resp = client.get(f"/api/accounts/{account_id}")
    assert detail_resp.status_code == 200
    data = detail_resp.json()
    assert "personality" in data
    assert data["personality"] is not None
    assert "formality" in data["personality"]
    assert "friendliness" in data["personality"]


def test_account_connect_and_disconnect(client: TestClient) -> None:
    """Connecting stores credentials securely; disconnecting revokes them."""
    seed_resp = client.post("/api/accounts/seed")
    biz_wa = next(a for a in seed_resp.json() if a["platform"] == "whatsapp" and a["account_type"] == "business")
    acc_id = biz_wa["id"]

    # Connect with access token
    connect_resp = client.post(
        f"/api/accounts/{acc_id}/connect",
        json={"credentials": "meta-eaab-secret-access-token-12345", "platform_account_id": "phone-num-id-9988"},
    )
    assert connect_resp.status_code == 200
    data = connect_resp.json()
    assert data["integration_status"] == "connected"
    assert data["has_credentials"] is True
    # Ensure sensitive credentials are never leaked in response
    assert "meta-eaab-secret-access-token-12345" not in connect_resp.text

    # Disconnect
    disconnect_resp = client.post(f"/api/accounts/{acc_id}/disconnect")
    assert disconnect_resp.status_code == 200
    disc_data = disconnect_resp.json()
    assert disc_data["integration_status"] == "disconnected"
    assert disc_data["has_credentials"] is False
    assert disc_data["automation_enabled"] is False


def test_update_account_personality(client: TestClient) -> None:
    """PATCH /api/accounts/{id}/personality modifies communication tone."""
    seed_resp = client.post("/api/accounts/seed")
    acc_id = seed_resp.json()[0]["id"]

    patch_resp = client.patch(
        f"/api/accounts/{acc_id}/personality",
        json={"formality": 0.95, "humour": 0.05, "reply_length": "medium", "hinglish_preference": 0.1},
    )
    assert patch_resp.status_code == 200
    p = patch_resp.json()
    assert p["formality"] == 0.95
    assert p["humour"] == 0.05
    assert p["reply_length"] == "medium"
    assert p["hinglish_preference"] == 0.1


def test_global_automation_controls(client: TestClient) -> None:
    """Test pause, resume, and emergency stop endpoints."""
    # Check settings
    settings_resp = client.get("/api/automation/settings")
    assert settings_resp.status_code == 200
    assert "global_paused" in settings_resp.json()

    # Pause
    pause_resp = client.post("/api/automation/pause")
    assert pause_resp.status_code == 200
    assert client.get("/api/automation/settings").json()["global_paused"] is True

    # Resume
    resume_resp = client.post("/api/automation/resume")
    assert resume_resp.status_code == 200
    assert client.get("/api/automation/settings").json()["global_paused"] is False

    # Emergency Stop
    stop_resp = client.post("/api/automation/emergency-stop")
    assert stop_resp.status_code == 200
    assert client.get("/api/automation/settings").json()["emergency_stopped"] is True

    # Resuming while emergency stop is active must fail
    fail_resume = client.post("/api/automation/resume")
    assert fail_resume.status_code == 400

    # Reset emergency stop
    client.post("/api/automation/reset-emergency-stop")
    assert client.get("/api/automation/settings").json()["emergency_stopped"] is False
    client.post("/api/automation/resume")

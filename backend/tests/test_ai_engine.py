"""
End-to-end integration tests for AI Engine API endpoints.
"""

from fastapi.testclient import TestClient


def test_ai_generate_reply_personal_whatsapp(client: TestClient) -> None:
    """POST /api/ai/generate-reply for Personal WhatsApp returns natural casual reply."""
    seed_resp = client.post("/api/accounts/seed")
    accounts = seed_resp.json()
    personal_acc = next(a for a in accounts if a["platform"] == "whatsapp" and a["account_type"] == "personal")

    req_payload = {
        "account_id": personal_acc["id"],
        "message": "Hey bhai, kya haal chal?",
        "sender_name": "Rohan",
        "conversation_history": [],
    }

    resp = client.post("/api/ai/generate-reply", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["mode"] == "personal"
    assert len(data["reply"]) > 0
    assert data["requires_human"] is False


def test_ai_generate_reply_business_bottle_advertising(client: TestClient) -> None:
    """POST /api/ai/generate-reply for Business WhatsApp answers bottle enquiry with qualification."""
    seed_resp = client.post("/api/accounts/seed")
    accounts = seed_resp.json()
    biz_acc = next(a for a in accounts if a["platform"] == "whatsapp" and a["account_type"] == "business")

    req_payload = {
        "account_id": biz_acc["id"],
        "message": "Hey, do you guys provide bottle advertising? What are your charges?",
        "sender_name": "Potential Client",
        "conversation_history": [],
        "business_context": "Bottle advertising across Mumbai and Delhi.",
    }

    resp = client.post("/api/ai/generate-reply", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["mode"] == "business"
    assert "bottle" in data["reply"].lower()
    assert data["requires_human"] is False


def test_ai_test_message_endpoint(client: TestClient) -> None:
    """POST /api/ai/test-message returns preview result along with system prompt used."""
    seed_resp = client.post("/api/accounts/seed")
    acc_id = seed_resp.json()[0]["id"]

    test_payload = {
        "account_id": acc_id,
        "message": "Hello, testing preview feature",
        "sender_name": "Tester",
    }

    resp = client.post("/api/ai/test-message", json=test_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["account_id"] == acc_id
    assert "result" in data
    assert "reply" in data["result"]
    assert "system_prompt_used" in data
    assert len(data["system_prompt_used"]) > 50


def test_ai_settings_endpoint(client: TestClient) -> None:
    """GET and PATCH /api/ai/settings inspect and dynamically update runtime provider configs."""
    get_resp = client.get("/api/ai/settings")
    assert get_resp.status_code == 200
    initial = get_resp.json()
    assert "provider" in initial
    assert "model" in initial

    # Patch temperature
    patch_resp = client.patch("/api/ai/settings", json={"temperature": 0.4})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["temperature"] == 0.4

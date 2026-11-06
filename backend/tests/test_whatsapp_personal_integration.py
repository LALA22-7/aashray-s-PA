"""
Tests for Personal WhatsApp Companion Bridge integration:
- Inbound message handling and personal AI reply generation
- Two-way sync: recording outbound messages typed by owner on physical phone
- Duplicate event rejection (idempotency)
- Approval mode draft queuing
- Bridge status and QR code retrieval endpoints
"""

from fastapi.testclient import TestClient


def test_personal_whatsapp_inbound_message_and_reply(client: TestClient) -> None:
    """POST /webhooks/whatsapp-personal processes inbound message and generates personal reply."""
    client.post("/api/accounts/seed")

    # Ensure Personal WhatsApp account has automatic mode for test
    accounts = client.get("/api/accounts").json()
    personal_wa = next(a for a in accounts if a["platform"] == "whatsapp" and a["account_type"] == "personal")
    client.patch(
        f"/api/accounts/{personal_wa['id']}/automation",
        json={"automation_mode": "automatic", "automation_enabled": True},
    )

    sample_payload = {
        "event": "message",
        "platform_message_id": "wa_pers_msg_001",
        "from": "919876543210",
        "sender_name": "Rohan Verma",
        "text": "Bro are you free for a catchup tonight?",
        "is_from_me": False,
        "timestamp": 1700000000,
    }

    resp = client.post("/webhooks/whatsapp-personal", json=sample_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["action"] == "send_automatic"

    # Verify conversation thread was created
    convs_resp = client.get("/api/conversations")
    assert convs_resp.status_code == 200
    convs = convs_resp.json()
    target_conv = next(
        c for c in convs if c["contact"] and c["contact"]["platform_contact_id"] == "919876543210"
    )
    assert target_conv is not None
    assert target_conv["message_count"] == 2

    # Verify messages
    msg_resp = client.get(f"/api/conversations/{target_conv['id']}/messages")
    messages = msg_resp.json()
    assert len(messages) == 2
    assert messages[0]["direction"] == "inbound"
    assert "catchup" in messages[0]["content"]
    assert messages[1]["direction"] == "outbound"
    assert messages[1]["is_ai_generated"] is True


def test_personal_whatsapp_owner_outgoing_sync(client: TestClient) -> None:
    """When Ashray types on his physical phone (is_from_me=True), message is recorded and no AI triggers."""
    client.post("/api/accounts/seed")

    owner_payload = {
        "event": "message",
        "platform_message_id": "wa_owner_msg_002",
        "from": "919876543210",
        "sender_name": "Rohan Verma",
        "text": "Yeah bro, let's meet at 8 PM at Cyber Hub.",
        "is_from_me": True,
        "timestamp": 1700000005,
    }

    resp = client.post("/webhooks/whatsapp-personal", json=owner_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "synced"
    assert data["direction"] == "outbound"

    # Verify message in thread has sender_type="owner" and is NOT ai_generated
    convs = client.get("/api/conversations").json()
    target_conv = next(
        c for c in convs if c["contact"] and c["contact"]["platform_contact_id"] == "919876543210"
    )
    messages = client.get(f"/api/conversations/{target_conv['id']}/messages").json()
    last_msg = messages[-1]
    assert last_msg["direction"] == "outbound"
    assert last_msg["sender_type"] == "owner"
    assert last_msg["is_ai_generated"] is False
    assert last_msg["owner_approved"] is True


def test_personal_whatsapp_webhook_deduplication(client: TestClient) -> None:
    """Duplicate message events from bridge are ignored."""
    client.post("/api/accounts/seed")

    dup_payload = {
        "event": "message",
        "platform_message_id": "wa_pers_dup_999",
        "from": "919999888877",
        "sender_name": "Sameer",
        "text": "Testing duplicate prevention",
        "is_from_me": False,
        "timestamp": 1700000010,
    }

    # First send -> success
    first_resp = client.post("/webhooks/whatsapp-personal", json=dup_payload)
    assert first_resp.status_code == 200
    assert first_resp.json()["status"] == "success"

    # Second send -> duplicate ignored
    second_resp = client.post("/webhooks/whatsapp-personal", json=dup_payload)
    assert second_resp.status_code == 200
    assert second_resp.json()["status"] == "duplicate_ignored"


def test_personal_whatsapp_approval_mode(client: TestClient) -> None:
    """When Personal WhatsApp account is in approval mode, drafts are queued without auto-sending."""
    client.post("/api/accounts/seed")

    # Set personal account to approval mode
    accounts = client.get("/api/accounts").json()
    personal_wa = next(a for a in accounts if a["platform"] == "whatsapp" and a["account_type"] == "personal")
    client.patch(
        f"/api/accounts/{personal_wa['id']}/automation",
        json={"automation_mode": "approval", "automation_status": "active"},
    )

    approval_payload = {
        "event": "message",
        "platform_message_id": "wa_pers_approval_001",
        "from": "919888777666",
        "sender_name": "Uncle Sharma",
        "text": "Beta how is your startup going?",
        "is_from_me": False,
        "timestamp": 1700000020,
    }

    resp = client.post("/webhooks/whatsapp-personal", json=approval_payload)
    assert resp.status_code == 200
    assert resp.json()["action"] == "queue_for_approval"

    # Verify pending draft message
    convs = client.get("/api/conversations").json()
    target_conv = next(
        c for c in convs if c["contact"] and c["contact"]["platform_contact_id"] == "919888777666"
    )
    messages = client.get(f"/api/conversations/{target_conv['id']}/messages").json()
    draft = messages[-1]
    assert draft["direction"] == "outbound"
    assert draft["delivery_status"] == "pending"
    assert draft["owner_approved"] is False


def test_personal_whatsapp_bridge_endpoints(client: TestClient) -> None:
    """Status and QR endpoints return structured JSON gracefully."""
    status_resp = client.get("/webhooks/whatsapp-personal/status")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert "status" in data

    qr_resp = client.get("/webhooks/whatsapp-personal/qr")
    assert qr_resp.status_code == 200
    qr_data = qr_resp.json()
    assert "status" in qr_data

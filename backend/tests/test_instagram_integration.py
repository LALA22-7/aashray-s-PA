"""
Tests for Meta Instagram Messaging API integration:
- Webhook verification handshake
- Inbound message processing & automated AI response dispatch
- Duplicate event rejection
- Echo message filtering
- Status receipts (delivery, read)
- HMAC signature verification
- Safety policy escalation on complaints
"""

import hashlib
import hmac

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.integrations.instagram.adapter import InstagramAdapter
from app.services.safety_service import SafetyService


def test_instagram_webhook_verification_handshake(client: TestClient) -> None:
    """GET /webhooks/instagram with valid verify_token echoes hub.challenge."""
    params = {
        "hub.mode": "subscribe",
        "hub.challenge": "instagram_challenge_token_8899",
        "hub.verify_token": "aashrays_pa_ig_verify_token",
    }
    resp = client.get("/webhooks/instagram", params=params)
    assert resp.status_code == 200
    assert resp.text == "instagram_challenge_token_8899"


def test_instagram_webhook_verification_invalid_token(client: TestClient) -> None:
    """GET /webhooks/instagram with wrong token returns 403 Forbidden."""
    params = {
        "hub.mode": "subscribe",
        "hub.challenge": "challenge_token_xyz",
        "hub.verify_token": "wrong_instagram_token",
    }
    resp = client.get("/webhooks/instagram", params=params)
    assert resp.status_code == 403


def test_instagram_inbound_message_processing_and_auto_reply(client: TestClient) -> None:
    """POST /webhooks/instagram processes inbound message and generates automatic reply."""
    client.post("/api/accounts/seed")
    client.post("/api/knowledge/seed")

    sample_payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "IG_PAGE_ID_7788",
                "time": 1700000000,
                "messaging": [
                    {
                        "sender": {"id": "ig_user_10203040"},
                        "recipient": {"id": "IG_PAGE_ID_7788"},
                        "timestamp": 1700000000,
                        "message": {
                            "mid": "m_mid_test_ig_inbound_001",
                            "text": "Hey, do you do bottle advertising for college festivals in Delhi? We need around 2000 bottles.",
                        },
                    }
                ],
            }
        ],
    }

    resp = client.post("/webhooks/instagram", json=sample_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["processed_messages"] == 1

    # Verify conversation thread was created
    convs_resp = client.get("/api/conversations")
    assert convs_resp.status_code == 200
    convs = convs_resp.json()
    assert len(convs) >= 1

    target_conv = next(
        c for c in convs if c["contact"] and c["contact"]["platform_contact_id"] == "ig_user_10203040"
    )
    assert target_conv is not None
    assert target_conv["message_count"] == 2  # Inbound + Outbound reply

    # Verify messages in thread
    msg_resp = client.get(f"/api/conversations/{target_conv['id']}/messages")
    messages = msg_resp.json()
    assert len(messages) == 2
    assert messages[0]["direction"] == "inbound"
    assert "bottle advertising" in messages[0]["content"]
    assert messages[1]["direction"] == "outbound"
    assert messages[1]["is_ai_generated"] is True
    assert "bottle" in messages[1]["content"].lower()

    # Verify lead was qualified and captured
    leads_resp = client.get("/api/leads")
    assert leads_resp.status_code == 200
    leads = leads_resp.json()
    assert len(leads) >= 1
    captured = next(lead_item for lead_item in leads if lead_item["conversation_id"] == target_conv["id"])
    assert "2000 bottles" in captured["enquiry"]
    assert "203040" in captured["customer_name"]


def test_instagram_webhook_deduplication(client: TestClient) -> None:
    """Duplicate Instagram webhook events are ignored."""
    client.post("/api/accounts/seed")

    dup_payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "IG_PAGE_ID_7788",
                "time": 1700000000,
                "messaging": [
                    {
                        "sender": {"id": "ig_user_dup_111"},
                        "recipient": {"id": "IG_PAGE_ID_7788"},
                        "timestamp": 1700000000,
                        "message": {
                            "mid": "m_mid_dup_test_999",
                            "text": "Hello! Testing Instagram deduplication.",
                        },
                    }
                ],
            }
        ],
    }

    # First delivery -> processed
    first_resp = client.post("/webhooks/instagram", json=dup_payload)
    assert first_resp.status_code == 200
    assert first_resp.json()["processed_messages"] == 1

    # Second delivery (retry) -> ignored due to idempotency
    second_resp = client.post("/webhooks/instagram", json=dup_payload)
    assert second_resp.status_code == 200
    assert second_resp.json()["processed_messages"] == 0


def test_instagram_echo_message_ignored(client: TestClient) -> None:
    """Echo messages from Instagram page owner are ignored to avoid infinite loops."""
    client.post("/api/accounts/seed")

    echo_payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "IG_PAGE_ID_7788",
                "time": 1700000000,
                "messaging": [
                    {
                        "sender": {"id": "IG_PAGE_ID_7788"},
                        "recipient": {"id": "ig_user_10203040"},
                        "timestamp": 1700000000,
                        "message": {
                            "mid": "m_mid_echo_001",
                            "is_echo": True,
                            "text": "Our manual human reply sent via Instagram App",
                        },
                    }
                ],
            }
        ],
    }

    resp = client.post("/webhooks/instagram", json=echo_payload)
    assert resp.status_code == 200
    assert resp.json()["processed_messages"] == 0


def test_instagram_status_receipt_update(client: TestClient, db_session: Session) -> None:
    """Read and delivery receipts update message status in DB."""
    client.post("/api/accounts/seed")

    mid_del = "m_mid_for_delivery_test"
    mid_read = "m_mid_for_read_test"

    safety = SafetyService(db_session)
    accounts = safety.account_repo.get_all()
    biz_ig = next(a for a in accounts if a.platform == "instagram" and a.account_type == "business")

    # Use manual-input to reliably build conversation
    manual_resp = client.post(
        "/api/conversations/manual-input",
        json={
            "account_id": biz_ig.id,
            "sender_contact_id": "ig_user_receipts",
            "message_content": "Initial message",
            "record_in_history": True,
        },
    )
    conv_id = manual_resp.json()["conversation_id"]

    # Append outbound messages with target MIDs
    client.post(
        f"/api/conversations/{conv_id}/messages",
        json={
            "content": "Outbound delivery msg",
            "direction": "outbound",
            "platform_message_id": mid_del,
            "delivery_status": "sent",
        },
    )
    client.post(
        f"/api/conversations/{conv_id}/messages",
        json={
            "content": "Outbound read msg",
            "direction": "outbound",
            "platform_message_id": mid_read,
            "delivery_status": "sent",
        },
    )

    # 1. Send delivery receipt
    delivery_payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "IG_PAGE_ID_7788",
                "messaging": [
                    {
                        "sender": {"id": "ig_user_receipts"},
                        "recipient": {"id": "IG_PAGE_ID_7788"},
                        "delivery": {"mids": [mid_del], "watermark": 1700000000},
                    }
                ],
            }
        ],
    }
    resp1 = client.post("/webhooks/instagram", json=delivery_payload)
    assert resp1.status_code == 200
    assert resp1.json()["status_updates"] >= 1

    # 2. Send read receipt
    read_payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "IG_PAGE_ID_7788",
                "messaging": [
                    {
                        "sender": {"id": "ig_user_receipts"},
                        "recipient": {"id": "IG_PAGE_ID_7788"},
                        "read": {"mid": mid_read, "watermark": 1700000000},
                    }
                ],
            }
        ],
    }
    resp2 = client.post("/webhooks/instagram", json=read_payload)
    assert resp2.status_code == 200
    assert resp2.json()["status_updates"] >= 1


def test_instagram_hmac_signature_validation(monkeypatch) -> None:
    """HMAC-SHA256 signature verification passes on matching hash and fails on tampered body."""
    secret = "my_instagram_app_secret_123"
    adapter = InstagramAdapter(app_secret=secret)

    raw_body = b'{"object":"instagram","entry":[]}'
    correct_sig = "sha256=" + hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()

    assert adapter.verify_signature(raw_body, correct_sig) is True
    assert adapter.verify_signature(raw_body, "sha256=invalidhexsignature00000") is False
    assert adapter.verify_signature(b'{"tampered":"body"}', correct_sig) is False


def test_instagram_policy_escalation(client: TestClient) -> None:
    """Inbound complaint on Instagram triggers policy escalation and queues draft instead of auto-sending."""
    client.post("/api/accounts/seed")

    complaint_payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "IG_PAGE_ID_7788",
                "time": 1700000000,
                "messaging": [
                    {
                        "sender": {"id": "ig_user_angry_customer"},
                        "recipient": {"id": "IG_PAGE_ID_7788"},
                        "timestamp": 1700000000,
                        "message": {
                            "mid": "m_mid_complaint_001",
                            "text": "The bottles for our event were completely damaged and labels peeled off! I want a full refund immediately!",
                        },
                    }
                ],
            }
        ],
    }

    resp = client.post("/webhooks/instagram", json=complaint_payload)
    assert resp.status_code == 200
    assert resp.json()["processed_messages"] == 1

    # Check conversation messages
    convs_resp = client.get("/api/conversations")
    target_conv = next(
        c for c in convs_resp.json() if c["contact"] and c["contact"]["platform_contact_id"] == "ig_user_angry_customer"
    )
    msg_resp = client.get(f"/api/conversations/{target_conv['id']}/messages")
    messages = msg_resp.json()
    assert len(messages) == 2

    outbound = messages[1]
    assert outbound["direction"] == "outbound"
    # Should NOT be automatically sent: delivery_status must be 'pending' and owner_approved must be False
    assert outbound["delivery_status"] == "pending"
    assert outbound["owner_approved"] is False
    assert outbound["ai_metadata"]["intent"] == "complaint"

"""
Integration tests for WhatsApp Cloud API Webhook verification, inbound parsing,
AI reply dispatch, and status updates.
"""

import hashlib
import hmac

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.integrations.whatsapp.adapter import WhatsAppAdapter
from app.services.safety_service import SafetyService


def test_whatsapp_webhook_verification_handshake(client: TestClient) -> None:
    """GET /webhooks/whatsapp validates hub.verify_token and returns hub.challenge."""
    settings = get_settings()
    verify_token = settings.WHATSAPP_VERIFY_TOKEN or "test-verify-token-xyz"

    # Temporarily set verify token on adapter test
    adapter = WhatsAppAdapter(verify_token=verify_token)
    assert adapter.verify_webhook_token("subscribe", verify_token, "challenge_code_12345") == "challenge_code_12345"

    # Test via HTTP endpoint
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": settings.WHATSAPP_VERIFY_TOKEN,
        "hub.challenge": "1155992288",
    }
    resp = client.get("/webhooks/whatsapp", params=params)
    assert resp.status_code == 200
    assert resp.text == "1155992288"


def test_whatsapp_webhook_verification_invalid_token(client: TestClient) -> None:
    """GET /webhooks/whatsapp with wrong token is rejected with 403 Forbidden."""
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "wrong-token-abc",
        "hub.challenge": "1155992288",
    }
    resp = client.get("/webhooks/whatsapp", params=params)
    assert resp.status_code == 403


def test_whatsapp_inbound_message_processing_and_auto_reply(
    client: TestClient, db_session: Session
) -> None:
    """POST /webhooks/whatsapp parses inbound message, records conversation, and auto-dispatches reply."""
    # Seed default accounts and knowledge
    client.post("/api/accounts/seed")
    client.post("/api/knowledge/seed")

    # Construct representative Meta Cloud API webhook payload
    sample_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "BIZ_ACCOUNT_9988",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "919988001122",
                                "phone_number_id": "PHONE_ID_BIZ_123",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Siddharth Verma"},
                                    "wa_id": "919876500000",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "919876500000",
                                    "id": "wamid.TEST_EVENT_ID_001",
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {
                                        "body": "Hi, do you provide bottle advertising? We need 3,000 bottles in Mumbai."
                                    },
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    resp = client.post("/webhooks/whatsapp", json=sample_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["processed_messages"] == 1

    # Verify conversation thread was created
    convs_resp = client.get("/api/conversations")
    assert convs_resp.status_code == 200
    convs = convs_resp.json()
    assert len(convs) >= 1

    # Find conversation for Siddharth
    target_conv = next(c for c in convs if c["contact"] and c["contact"]["platform_contact_id"] == "919876500000")
    assert target_conv is not None
    assert target_conv["message_count"] == 2  # Inbound + Outbound reply

    # Verify messages in thread
    msg_resp = client.get(f"/api/conversations/{target_conv['id']}/messages")
    messages = msg_resp.json()
    assert len(messages) == 2
    assert messages[0]["direction"] == "inbound"
    assert "3,000 bottles" in messages[0]["content"]
    assert messages[1]["direction"] == "outbound"
    assert messages[1]["is_ai_generated"] is True
    assert "bottle" in messages[1]["content"].lower()

    # Verify lead was qualified and captured
    leads_resp = client.get("/api/leads")
    assert leads_resp.status_code == 200
    leads = leads_resp.json()
    assert len(leads) >= 1
    captured = next(lead_item for lead_item in leads if lead_item["conversation_id"] == target_conv["id"])
    assert captured["customer_name"] == "Siddharth Verma"


def test_whatsapp_webhook_deduplication(client: TestClient) -> None:
    """Duplicate webhook events from Meta are ignored."""
    client.post("/api/accounts/seed")

    dup_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "BIZ_ACCOUNT_9988",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "919988001122",
                                "phone_number_id": "PHONE_ID_BIZ_123",
                            },
                            "messages": [
                                {
                                    "from": "919876500000",
                                    "id": "wamid.TEST_DUP_ID_999",
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": "Testing duplicate prevention"},
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    # First send -> processed
    first_resp = client.post("/webhooks/whatsapp", json=dup_payload)
    assert first_resp.status_code == 200
    assert first_resp.json()["processed_messages"] == 1

    # Second send (retry) -> ignored due to deduplication
    second_resp = client.post("/webhooks/whatsapp", json=dup_payload)
    assert second_resp.status_code == 200
    assert second_resp.json()["processed_messages"] == 0


def test_whatsapp_status_receipt_update(client: TestClient, db_session: Session) -> None:
    """POST /webhooks/whatsapp with statuses updates delivery status of existing messages."""
    client.post("/api/accounts/seed")

    # 1. Create an outbound message with a known WAMID
    wamid = "wamid.KNOWN_MESSAGE_ID_777"
    safety = SafetyService(db_session)
    accounts = safety.account_repo.get_all()
    biz_wa = next(a for a in accounts if a.platform == "whatsapp" and a.account_type == "business")

    # Use manual-input to reliably build conversation
    manual_resp = client.post(
        "/api/conversations/manual-input",
        json={
            "account_id": biz_wa.id,
            "sender_contact_id": "9199990000",
            "message_content": "Initial message",
            "record_in_history": True,
        },
    )
    conv_id = manual_resp.json()["conversation_id"]

    # Append outbound message with target WAMID
    client.post(
        f"/api/conversations/{conv_id}/messages",
        json={
            "content": "Outbound reply pending delivery",
            "direction": "outbound",
            "platform_message_id": wamid,
            "delivery_status": "sent",
        },
    )

    # 2. Receive delivery receipt webhook from Meta
    status_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "BIZ_ACCOUNT_9988",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "919988001122",
                                "phone_number_id": "PHONE_ID_BIZ_123",
                            },
                            "statuses": [
                                {
                                    "id": wamid,
                                    "status": "delivered",
                                    "timestamp": "1700000005",
                                    "recipient_id": "9199990000",
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    status_resp = client.post("/webhooks/whatsapp", json=status_payload)
    assert status_resp.status_code == 200
    assert status_resp.json()["status_updates"] == 1

    # Verify message status updated to 'delivered'
    msgs = client.get(f"/api/conversations/{conv_id}/messages").json()
    updated_msg = next(m for m in msgs if m["platform_message_id"] == wamid)
    assert updated_msg["delivery_status"] == "delivered"


def test_hmac_signature_validation() -> None:
    """Verify HMAC SHA-256 signature computation and comparison."""
    secret = "meta_app_secret_12345"
    payload = b'{"object":"whatsapp_business_account"}'
    adapter = WhatsAppAdapter(app_secret=secret)

    # Valid signature
    valid_sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert adapter.verify_signature(payload, valid_sig) is True

    # Invalid signature
    assert adapter.verify_signature(payload, "sha256=invalid_hash_value") is False
    assert adapter.verify_signature(payload, "corrupted_header") is False

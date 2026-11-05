"""
Tests for Conversation lifecycle, context building, and manual workflows.
"""

from fastapi.testclient import TestClient


def test_manual_message_workflow_personal_whatsapp(client: TestClient) -> None:
    """POST /api/conversations/manual-input handles AI-assisted manual replies."""
    seed_resp = client.post("/api/accounts/seed")
    accounts = seed_resp.json()
    personal_wa = next(a for a in accounts if a["platform"] == "whatsapp" and a["account_type"] == "personal")

    req = {
        "account_id": personal_wa["id"],
        "sender_contact_id": "+919876543210",
        "sender_name": "Aman",
        "message_content": "Bhai, weekend pe mil rahe hain kya?",
        "record_in_history": True,
    }

    resp = client.post("/api/conversations/manual-input", json=req)
    assert resp.status_code == 200
    data = resp.json()

    assert "conversation_id" in data
    assert len(data["copyable_text"]) > 0
    assert data["suggested_reply"]["mode"] == "personal"

    # Verify conversation thread was created and contains the message
    conv_resp = client.get(f"/api/conversations/{data['conversation_id']}")
    assert conv_resp.status_code == 200
    conv = conv_resp.json()
    assert conv["message_count"] == 1
    assert conv["messages"][0]["content"] == "Bhai, weekend pe mil rahe hain kya?"


def test_conversation_reply_with_sliding_window(client: TestClient) -> None:
    """POST /api/conversations/{id}/reply uses prior messages as context."""
    seed_resp = client.post("/api/accounts/seed")
    accounts = seed_resp.json()
    biz_wa = next(a for a in accounts if a["platform"] == "whatsapp" and a["account_type"] == "business")

    # Seed business knowledge
    client.post("/api/knowledge/seed")

    # 1. First message from client
    manual_resp = client.post(
        "/api/conversations/manual-input",
        json={
            "account_id": biz_wa["id"],
            "sender_contact_id": "corporate_client_1",
            "sender_name": "Priya",
            "message_content": "Hi, we need custom branded bottles for our annual summit.",
            "record_in_history": True,
        },
    )
    conv_id = manual_resp.json()["conversation_id"]

    # 2. Add assistant response to history
    client.post(
        f"/api/conversations/{conv_id}/messages",
        json={
            "content": "Hi Priya! We'd love to help. How many bottles are you looking at, and what's your event location?",
            "direction": "outbound",
            "sender_type": "assistant",
        },
    )

    # 3. Add client followup
    client.post(
        f"/api/conversations/{conv_id}/messages",
        json={
            "content": "Around 2,000 bottles in Mumbai. What would be the cost?",
            "direction": "inbound",
            "sender_type": "contact",
        },
    )

    # 4. Trigger AI reply with auto-save
    reply_resp = client.post(
        f"/api/conversations/{conv_id}/reply",
        json={"auto_save_outbound": True},
    )
    assert reply_resp.status_code == 200
    ai_reply = reply_resp.json()
    assert ai_reply["mode"] == "business"
    assert len(ai_reply["reply"]) > 10

    # Verify thread now contains all 4 messages
    updated_conv = client.get(f"/api/conversations/{conv_id}").json()
    assert updated_conv["message_count"] == 4


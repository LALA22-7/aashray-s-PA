"""
Automated tests for strict cross-account isolation in Phase 2.
"""

from fastapi.testclient import TestClient

from app.utils.encryption import decrypt_data, encrypt_data


def test_personality_isolation_between_accounts(client: TestClient) -> None:
    """Modifying personality in Account A must not alter Account B."""
    seed_resp = client.post("/api/accounts/seed")
    accounts = seed_resp.json()

    wa_personal = next(a for a in accounts if a["platform"] == "whatsapp" and a["account_type"] == "personal")
    wa_business = next(a for a in accounts if a["platform"] == "whatsapp" and a["account_type"] == "business")

    # Record initial business personality
    biz_initial = client.get(f"/api/accounts/{wa_business['id']}/personality").json()

    # Heavily customize personal personality
    patch_resp = client.patch(
        f"/api/accounts/{wa_personal['id']}/personality",
        json={
            "formality": 0.05,
            "humour": 0.95,
            "reply_length": "short",
            "hinglish_preference": 0.9,
            "system_prompt_override": "Custom Personal Override",
        },
    )
    assert patch_resp.status_code == 200

    # Verify personal personality changed
    personal_updated = client.get(f"/api/accounts/{wa_personal['id']}/personality").json()
    assert personal_updated["formality"] == 0.05
    assert personal_updated["humour"] == 0.95
    assert personal_updated["system_prompt_override"] == "Custom Personal Override"

    # Verify business personality remained completely untouched
    biz_after = client.get(f"/api/accounts/{wa_business['id']}/personality").json()
    assert biz_after["formality"] == biz_initial["formality"]
    assert biz_after["humour"] == biz_initial["humour"]
    assert biz_after["system_prompt_override"] == biz_initial["system_prompt_override"]


def test_automation_settings_isolation(client: TestClient) -> None:
    """Updating automation mode on one account must not modify another."""
    seed_resp = client.post("/api/accounts/seed")
    accounts = seed_resp.json()

    ig_personal = next(a for a in accounts if a["platform"] == "instagram" and a["account_type"] == "personal")
    ig_business = next(a for a in accounts if a["platform"] == "instagram" and a["account_type"] == "business")

    # Update personal to disabled
    client.patch(
        f"/api/accounts/{ig_personal['id']}",
        json={"automation_enabled": False, "automation_mode": "disabled"},
    )

    # Update business to automatic
    client.patch(
        f"/api/accounts/{ig_business['id']}",
        json={"automation_enabled": True, "automation_mode": "automatic"},
    )

    p_check = client.get(f"/api/accounts/{ig_personal['id']}").json()
    b_check = client.get(f"/api/accounts/{ig_business['id']}").json()

    assert p_check["automation_enabled"] is False
    assert p_check["automation_mode"] == "disabled"

    assert b_check["automation_enabled"] is True
    assert b_check["automation_mode"] == "automatic"


def test_credential_encryption_isolation() -> None:
    """Verify encryption and decryption roundtrip integrity."""
    token_1 = "token_for_business_whatsapp_98765"
    token_2 = "token_for_business_instagram_12345"

    encrypted_1 = encrypt_data(token_1)
    encrypted_2 = encrypt_data(token_2)

    assert encrypted_1 != token_1
    assert encrypted_2 != token_2
    assert encrypted_1 != encrypted_2

    assert decrypt_data(encrypted_1) == token_1
    assert decrypt_data(encrypted_2) == token_2

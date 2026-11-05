"""
Tests for Business Knowledge Base management and prompt compilation.
"""

from fastapi.testclient import TestClient


def test_seed_and_list_knowledge(client: TestClient) -> None:
    """POST /api/knowledge/seed populates verified bottle advertising facts."""
    seed_resp = client.post("/api/knowledge/seed")
    assert seed_resp.status_code == 200
    assert seed_resp.json()["status"] == "success"

    # List items
    list_resp = client.get("/api/knowledge")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) >= 7

    # Check categories
    categories = {item["category"] for item in items}
    assert "agency_info" in categories
    assert "service" in categories
    assert "pricing" in categories
    assert "moq" in categories


def test_create_and_update_knowledge(client: TestClient) -> None:
    """Owner can add new pricing packages and edit them from the dashboard."""
    new_entry = {
        "category": "package",
        "title": "Corporate Tech Summit Special",
        "content": "Special bundle of 2,000 custom matte bottles with QR codes for ₹45,000 all inclusive.",
        "is_active": True,
        "priority": 95,
    }

    create_resp = client.post("/api/knowledge", json=new_entry)
    assert create_resp.status_code == 201
    item_id = create_resp.json()["id"]

    # Update content
    patch_resp = client.patch(
        f"/api/knowledge/{item_id}",
        json={"content": "Updated bundle: 2,500 matte bottles with QR codes for ₹50,000."},
    )
    assert patch_resp.status_code == 200
    assert "2,500 matte bottles" in patch_resp.json()["content"]


def test_knowledge_summary_and_compilation(client: TestClient) -> None:
    """GET /api/knowledge/summary provides compiled preview used in prompts."""
    client.post("/api/knowledge/seed")
    summary_resp = client.get("/api/knowledge/summary")
    assert summary_resp.status_code == 200
    data = summary_resp.json()

    assert data["total_items"] >= 7
    assert data["active_items"] >= 7
    assert "Bottle Advertising" in data["compiled_preview"]

"""Integration tests for FastAPI dashboard and preferences endpoints."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_dashboard_page_loads_correctly():
    """Validates that the dashboard HTML page renders with 200 OK."""
    response = client.get("/")
    assert response.status_code == 200
    assert "DevOps &amp; TBD Dashboard" in response.text
    assert "dark_mode_enabled" in response.text
    assert "/static/css/style.css" in response.text


def test_get_features_endpoint():
    """Validates /api/features endpoint returns correct schema."""
    response = client.get("/api/features?user_id=test_user")
    assert response.status_code == 200
    data = response.json()
    assert "flag_key" in data
    assert "is_enabled" in data
    assert "active_stage" in data


def test_user_preference_persistence_flow():
    """Ticket 3: Validates saving and reading user theme preferences."""
    user_id = "test_qa_user_42"

    # Save preference
    post_res = client.post(
        "/api/user/preferences",
        json={"user_id": user_id, "theme": "dark"},
    )
    assert post_res.status_code == 200
    assert post_res.json()["status"] == "success"

    # Read preference
    get_res = client.get(f"/api/user/preferences?user_id={user_id}")
    assert get_res.status_code == 200
    assert get_res.json()["theme"] == "dark"


def test_admin_toggle_simulation():
    """Validates switching simulation stages."""
    res = client.post(
        "/api/admin/toggle-simulation",
        json={"stage": "ticket_2"},
    )
    assert res.status_code == 200
    assert res.json()["active_stage"] == "ticket_2"

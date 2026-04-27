import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test."""
    original = {name: {**data, "participants": list(data["participants"])} for name, data in activities.items()}
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_all():
    # Arrange — no setup needed, default state is sufficient

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_get_activities_has_expected_fields():
    # Arrange — no setup needed

    # Act
    activity = client.get("/activities").json()["Chess Club"]

    # Assert
    for field in ("description", "schedule", "max_participants", "participants"):
        assert field in activity


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    # Arrange
    email = "new@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant():
    # Arrange
    email = "new@mergington.edu"
    activity_name = "Chess Club"

    # Act
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email in participants


def test_signup_activity_not_found():
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post("/activities/Nonexistent Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_signup_duplicate_participant():
    # Arrange
    email = "dup@mergington.edu"
    activity_name = "Chess Club"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


# --- DELETE /activities/{activity_name}/unregister ---

def test_unregister_success():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_activity_not_found():
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete("/activities/Nonexistent Club/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_unregister_participant_not_signed_up():
    # Arrange
    email = "nobody@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()

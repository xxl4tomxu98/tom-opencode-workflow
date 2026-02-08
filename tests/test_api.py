import pytest
from fastapi.testclient import TestClient


def test_create_todo(client):
    response = client.post(
        "/api/todos",
        json={
            "title": "Test todo",
            "phase": "planning",
            "priority": "medium",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test todo"
    assert data["phase"] == "planning"
    assert "id" in data
    assert "recommended_skills" in data


def test_list_todos(client):
    client.post(
        "/api/todos",
        json={"title": "One", "phase": "planning", "priority": "low"},
    )
    client.post(
        "/api/todos",
        json={"title": "Two", "phase": "design", "priority": "high"},
    )

    response = client.get("/api/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_todos_filter_by_phase(client):
    client.post(
        "/api/todos",
        json={"title": "Planning", "phase": "planning", "priority": "low"},
    )
    client.post(
        "/api/todos",
        json={"title": "Design", "phase": "design", "priority": "low"},
    )

    response = client.get("/api/todos?phase=planning")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Planning"


def test_get_todo(client):
    create_response = client.post(
        "/api/todos",
        json={"title": "Get me", "phase": "implementation", "priority": "high"},
    )
    todo_id = create_response.json()["id"]

    response = client.get(f"/api/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Get me"
    assert len(data["recommended_skills"]) >= 1


def test_get_todo_not_found(client):
    response = client.get("/api/todos/999")
    assert response.status_code == 404


def test_update_todo(client):
    create_response = client.post(
        "/api/todos",
        json={"title": "Original", "phase": "planning", "priority": "low"},
    )
    todo_id = create_response.json()["id"]

    response = client.put(
        f"/api/todos/{todo_id}",
        json={"title": "Updated", "priority": "high"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["priority"] == "high"


def test_delete_todo(client):
    create_response = client.post(
        "/api/todos",
        json={"title": "Delete me", "phase": "testing", "priority": "low"},
    )
    todo_id = create_response.json()["id"]

    response = client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/todos/{todo_id}")
    assert get_response.status_code == 404


def test_toggle_complete(client):
    create_response = client.post(
        "/api/todos",
        json={"title": "Toggle", "phase": "deployment", "priority": "medium"},
    )
    todo_id = create_response.json()["id"]
    assert create_response.json()["completed"] is False

    response = client.patch(f"/api/todos/{todo_id}/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_list_phases(client):
    response = client.get("/api/phases")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    phase_names = [p["name"] for p in data]
    assert "planning" in phase_names
    assert "deployment" in phase_names


def test_get_phase(client):
    response = client.get("/api/phases/implementation")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "implementation"
    assert len(data["skills"]) >= 1


def test_get_phase_not_found(client):
    response = client.get("/api/phases/invalid")
    assert response.status_code == 404

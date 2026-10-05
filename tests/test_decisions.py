from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_decision() -> None:
    response = client.post(
        "/v1/decisions",
        json={
            "objective": "Assess whether this supplier should be retained.",
            "context": "Supplier has experienced repeated delivery delays.",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body
    assert body["status"] == "pending"
    assert "created_at" in body
    assert "updated_at" in body


def test_create_decision_requires_objective() -> None:
    response = client.post(
        "/v1/decisions",
        json={
            "objective": "",
        },
    )

    assert response.status_code == 422

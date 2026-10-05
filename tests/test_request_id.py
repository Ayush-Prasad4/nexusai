from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_request_id_is_generated() -> None:
    response = client.get("/v1/health/live")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]


def test_request_id_is_preserved() -> None:
    request_id = "test-request-123"

    response = client.get(
        "/v1/health/live",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_liveness_check() -> None:
    response = client.get("/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_check() -> None:
    response = client.get("/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

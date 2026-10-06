from fastapi.testclient import TestClient

from app.main import app


def test_liveness_check() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_check() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_check_returns_503_when_redis_is_unavailable(
    monkeypatch,
) -> None:
    async def failing_ping() -> None:
        raise RuntimeError("Redis unavailable")

    with TestClient(app) as client:
        monkeypatch.setattr(
            client.app.state.redis,
            "ping",
            failing_ping,
        )

        response = client.get("/v1/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}


def test_readiness_check_returns_503_when_database_is_unavailable(
    monkeypatch,
) -> None:
    class FailingConnection:
        async def __aenter__(self):
            raise RuntimeError("Database unavailable")

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FailingEngine:
        def connect(self):
            return FailingConnection()

    monkeypatch.setattr(
        "app.api.v1.health.engine",
        FailingEngine(),
    )

    with TestClient(app) as client:
        response = client.get("/v1/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}


def test_liveness_check_does_not_depend_on_database_or_redis() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

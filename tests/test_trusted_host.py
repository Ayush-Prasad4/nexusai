from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.middleware.trusted_host import (
    add_trusted_host_middleware,
)


def create_app() -> FastAPI:
    app = FastAPI()

    add_trusted_host_middleware(app)

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    return app


def test_allowed_host_is_accepted() -> None:
    with TestClient(create_app()) as client:
        response = client.get(
            "/test",
            headers={"Host": "testserver"},
        )

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_localhost_is_accepted() -> None:
    with TestClient(create_app()) as client:
        response = client.get(
            "/test",
            headers={"Host": "localhost"},
        )

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_untrusted_host_is_rejected() -> None:
    with TestClient(create_app()) as client:
        response = client.get(
            "/test",
            headers={"Host": "malicious.example"},
        )

    assert response.status_code == 400
    assert response.text == "Invalid host header"

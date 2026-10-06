from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.middleware.request_size import RequestSizeLimitMiddleware


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestSizeLimitMiddleware)

    @app.post("/test")
    async def test_endpoint():
        return {"ok": True}

    return app


def test_request_within_size_limit_is_allowed(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.core.config.get_settings",
        lambda: type(
            "Settings",
            (),
            {"max_request_body_bytes": 100},
        )(),
    )

    with TestClient(create_app()) as client:
        response = client.post(
            "/test",
            content=b"x" * 100,
            headers={"Content-Length": "100"},
        )

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_request_above_size_limit_is_rejected(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.core.config.get_settings",
        lambda: type(
            "Settings",
            (),
            {"max_request_body_bytes": 100},
        )(),
    )

    with TestClient(create_app()) as client:
        response = client.post(
            "/test",
            content=b"x" * 101,
            headers={"Content-Length": "101"},
        )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Request body too large.",
    }


def test_invalid_content_length_is_rejected(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.core.config.get_settings",
        lambda: type(
            "Settings",
            (),
            {"max_request_body_bytes": 100},
        )(),
    )

    with TestClient(create_app()) as client:
        response = client.post(
            "/test",
            content=b"x",
            headers={"Content-Length": "invalid"},
        )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid Content-Length header.",
    }

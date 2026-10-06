import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors.handlers import unhandled_exception_handler


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )

    @app.get("/boom")
    async def boom():
        raise RuntimeError("database password=super-secret")

    return app


def test_unhandled_exception_returns_safe_response(
    caplog,
) -> None:
    with TestClient(create_app(), raise_server_exceptions=False) as client:
        with caplog.at_level(logging.ERROR):
            response = client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "internal_server_error",
            "message": "An internal server error occurred.",
        }
    }

    assert "database password=super-secret" in caplog.text
    assert "database password=super-secret" not in response.text

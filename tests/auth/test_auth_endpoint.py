from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_auth_me_requires_authentication() -> None:
    response = client.get("/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_auth_me_accepts_valid_token() -> None:
    with patch(
        "app.api.auth.decode_access_token",
        return_value="user-123",
    ):
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code == 200
    assert response.json() == {"user_id": "user-123"}


def test_auth_me_rejects_invalid_token() -> None:
    from app.application.auth.tokens import InvalidTokenError

    with patch(
        "app.api.auth.decode_access_token",
        side_effect=InvalidTokenError("invalid"),
    ):
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    assert response.headers["WWW-Authenticate"] == "Bearer"

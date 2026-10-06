from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.auth import get_current_user
from app.domain.models import User
from app.main import app


client = TestClient(app)


def test_auth_me_requires_authentication() -> None:
    response = client.get("/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_auth_me_returns_current_user() -> None:
    user = User(
        id=uuid4(),
        email="user@nexusai.test",
        password_hash="hashed-password",
        role="user",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    async def override_get_current_user() -> User:
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer valid-token"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(user.id)
    assert data["email"] == user.email
    assert data["role"] == user.role
    assert data["is_active"] is True
    assert "password_hash" not in data


def test_auth_me_does_not_expose_password_hash() -> None:
    user = User(
        id=uuid4(),
        email="safe@nexusai.test",
        password_hash="super-secret-hash",
        role="user",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    async def override_get_current_user() -> User:
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer valid-token"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "password_hash" not in response.json()
    assert "super-secret-hash" not in response.text


def test_auth_me_rejects_malformed_access_token() -> None:
    response = client.get(
        "/v1/auth/me",
        headers={"Authorization": "Bearer definitely-not-a-jwt"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid authentication credentials"
    )
    assert response.headers["WWW-Authenticate"] == "Bearer"

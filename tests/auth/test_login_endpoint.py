from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import get_user_repository
from app.application.auth.passwords import hash_password
from app.application.auth.tokens import decode_access_token
from app.main import app
from app.domain.models import User


class FakeUserRepository:
    def __init__(self, users: list[User] | None = None) -> None:
        self.users = {
            user.email: user
            for user in (users or [])
        }

    async def create(self, user: User) -> User:
        self.users[user.email] = user
        return user

    async def get_by_id(self, user_id):
        return next(
            (
                user
                for user in self.users.values()
                if user.id == user_id
            ),
            None,
        )

    async def get_by_email(self, email: str):
        return self.users.get(email)


def make_user(
    email: str = "ayush@example.com",
    password: str = "SuperSecret123!",
) -> User:
    now = datetime.now(timezone.utc)

    return User(
        id=uuid4(),
        email=email,
        password_hash=hash_password(password),
        created_at=now,
        updated_at=now,
    )


def test_login_endpoint_returns_access_token():
    user = make_user()
    repository = FakeUserRepository([user])

    app.dependency_overrides[get_user_repository] = (
        lambda: repository
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/v1/auth/login",
            json={
                "email": user.email,
                "password": "SuperSecret123!",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert decode_access_token(data["access_token"]) == str(user.id)

    finally:
        app.dependency_overrides.clear()


def test_login_endpoint_rejects_invalid_password():
    user = make_user()
    repository = FakeUserRepository([user])

    app.dependency_overrides[get_user_repository] = (
        lambda: repository
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/v1/auth/login",
            json={
                "email": user.email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == (
            "Invalid email or password"
        )
        assert response.headers["WWW-Authenticate"] == "Bearer"

    finally:
        app.dependency_overrides.clear()


def test_login_endpoint_rejects_unknown_email():
    repository = FakeUserRepository()

    app.dependency_overrides[get_user_repository] = (
        lambda: repository
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/v1/auth/login",
            json={
                "email": "unknown@example.com",
                "password": "SuperSecret123!",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == (
            "Invalid email or password"
        )

    finally:
        app.dependency_overrides.clear()

from fastapi.testclient import TestClient

from app.api.dependencies import get_user_repository
from app.main import app
from app.domain.models import User


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

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


def test_register_endpoint_creates_user():
    repository = FakeUserRepository()

    app.dependency_overrides[get_user_repository] = (
        lambda: repository
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/v1/auth/register",
            json={
                "email": "ayush@example.com",
                "password": "SuperSecret123!",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["email"] == "ayush@example.com"
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert "password" not in data
        assert "password_hash" not in data

        assert "ayush@example.com" in repository.users

    finally:
        app.dependency_overrides.clear()


def test_register_endpoint_rejects_duplicate_email():
    repository = FakeUserRepository()

    app.dependency_overrides[get_user_repository] = (
        lambda: repository
    )

    try:
        client = TestClient(app)

        payload = {
            "email": "ayush@example.com",
            "password": "SuperSecret123!",
        }

        first_response = client.post(
            "/v1/auth/register",
            json=payload,
        )

        second_response = client.post(
            "/v1/auth/register",
            json=payload,
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json()["detail"] == (
            "User with this email already exists"
        )

    finally:
        app.dependency_overrides.clear()

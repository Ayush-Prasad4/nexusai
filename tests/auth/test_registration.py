from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.application.auth.passwords import verify_password
from app.application.auth.registration import RegistrationService
from app.domain.models import User


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    async def create(self, user: User) -> User:
        self.users[user.email] = user
        return user

    async def get_by_id(self, user_id):
        return next(
            (user for user in self.users.values() if user.id == user_id),
            None,
        )

    async def get_by_email(self, email: str):
        return self.users.get(email)


@pytest.mark.asyncio
async def test_register_creates_hashed_password():
    repository = FakeUserRepository()
    service = RegistrationService(repository)

    user = await service.register(
        email="ayush@example.com",
        password="SuperSecret123!",
    )

    assert user.email == "ayush@example.com"
    assert user.password_hash != "SuperSecret123!"
    assert verify_password(
        "SuperSecret123!",
        user.password_hash,
    )
    assert user.role == "user"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_register_rejects_existing_email():
    repository = FakeUserRepository()

    existing_user = User(
        id=uuid4(),
        email="ayush@example.com",
        password_hash="existing-hash",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repository.users[existing_user.email] = existing_user

    service = RegistrationService(repository)

    with pytest.raises(
        ValueError,
        match="User with this email already exists",
    ):
        await service.register(
            email="ayush@example.com",
            password="AnotherPassword123!",
        )

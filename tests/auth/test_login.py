from datetime import datetime, timezone
from uuid import uuid4

import jwt
import pytest

from app.application.auth.login import (
    AuthenticationError,
    LoginService,
)
from app.application.auth.passwords import hash_password
from app.application.auth.tokens import decode_access_token
from app.core.config import get_settings
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
    is_active: bool = True,
) -> User:
    now = datetime.now(timezone.utc)

    return User(
        id=uuid4(),
        email=email,
        password_hash=hash_password(password),
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_login_returns_access_token_for_valid_credentials():
    user = make_user()
    repository = FakeUserRepository([user])
    service = LoginService(repository)

    token = await service.login(
        email=user.email,
        password="SuperSecret123!",
    )

    assert isinstance(token, str)
    assert decode_access_token(token) == str(user.id)


@pytest.mark.asyncio
async def test_login_rejects_wrong_password():
    user = make_user()
    repository = FakeUserRepository([user])
    service = LoginService(repository)

    with pytest.raises(
        AuthenticationError,
        match="Invalid email or password",
    ):
        await service.login(
            email=user.email,
            password="WrongPassword123!",
        )


@pytest.mark.asyncio
async def test_login_rejects_unknown_email():
    repository = FakeUserRepository()
    service = LoginService(repository)

    with pytest.raises(
        AuthenticationError,
        match="Invalid email or password",
    ):
        await service.login(
            email="unknown@example.com",
            password="SuperSecret123!",
        )


@pytest.mark.asyncio
async def test_login_rejects_inactive_user():
    user = make_user(is_active=False)
    repository = FakeUserRepository([user])
    service = LoginService(repository)

    with pytest.raises(
        AuthenticationError,
        match="Invalid email or password",
    ):
        await service.login(
            email=user.email,
            password="SuperSecret123!",
        )

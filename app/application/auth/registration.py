from datetime import datetime, timezone

from app.application.auth.passwords import hash_password
from app.domain.models import User
from app.domain.repositories import UserRepository


class RegistrationService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def register(
        self,
        email: str,
        password: str,
    ) -> User:
        existing_user = await self.user_repository.get_by_email(email)

        if existing_user is not None:
            raise ValueError("User with this email already exists")

        now = datetime.now(timezone.utc)

        user = User(
            email=email,
            password_hash=hash_password(password),
            created_at=now,
            updated_at=now,
        )

        return await self.user_repository.create(user)

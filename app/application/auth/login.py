from app.application.auth.passwords import verify_password
from app.application.auth.tokens import create_access_token
from app.domain.repositories import UserRepository


class AuthenticationError(Exception):
    """Raised when user authentication fails."""


class LoginService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def login(
        self,
        email: str,
        password: str,
    ) -> str:
        user = await self.user_repository.get_by_email(email)

        if user is None:
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        return create_access_token(str(user.id))

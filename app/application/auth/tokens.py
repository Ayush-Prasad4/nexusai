from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import get_settings


class InvalidTokenError(Exception):
    """Raised when an access token cannot be validated."""


def create_access_token(subject: str) -> str:
    settings = get_settings()

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> str:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError("Invalid access token") from exc

    subject = payload.get("sub")

    if not isinstance(subject, str) or not subject:
        raise InvalidTokenError("Access token subject is missing")

    return subject

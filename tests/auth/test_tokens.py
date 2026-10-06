import pytest

from app.application.auth.tokens import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
)


def test_access_token_round_trip() -> None:
    token = create_access_token("user-123")

    assert decode_access_token(token) == "user-123"


def test_invalid_token_is_rejected() -> None:
    with pytest.raises(InvalidTokenError):
        decode_access_token("not-a-valid-token")


def test_tampered_access_token_is_rejected() -> None:
    token = create_access_token("user-123")

    header, payload, signature = token.split(".")

    tampered_payload = (
        payload[:-1] + ("A" if payload[-1] != "A" else "B")
    )
    tampered_token = ".".join(
        [header, tampered_payload, signature]
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(tampered_token)


def test_access_token_without_subject_is_rejected() -> None:
    import jwt

    from app.core.config import get_settings

    settings = get_settings()

    token = jwt.encode(
        {"role": "user"},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_access_token_with_empty_subject_is_rejected() -> None:
    import jwt

    from app.core.config import get_settings

    settings = get_settings()

    token = jwt.encode(
        {"sub": ""},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_access_token_signed_with_wrong_secret_is_rejected() -> None:
    import jwt

    from app.core.config import get_settings

    settings = get_settings()

    token = jwt.encode(
        {"sub": "user-123"},
        "completely-different-secret-that-is-long-enough",
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_access_token_with_unsupported_algorithm_is_rejected() -> None:
    import jwt

    from app.core.config import get_settings

    settings = get_settings()

    token = jwt.encode(
        {"sub": "user-123"},
        "completely-different-secret-that-is-long-enough",
        algorithm="HS384",
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)

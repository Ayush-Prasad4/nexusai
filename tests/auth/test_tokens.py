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

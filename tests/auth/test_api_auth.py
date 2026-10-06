from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.api.auth import get_current_user


@pytest.mark.asyncio
async def test_get_current_user_returns_subject() -> None:
    with patch(
        "app.api.auth.decode_access_token",
        return_value="user-123",
    ):
        result = await get_current_user("valid-token")

    assert result == "user-123"


@pytest.mark.asyncio
async def test_get_current_user_rejects_invalid_token() -> None:
    from app.application.auth.tokens import InvalidTokenError

    with patch(
        "app.api.auth.decode_access_token",
        side_effect=InvalidTokenError("invalid"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid-token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"

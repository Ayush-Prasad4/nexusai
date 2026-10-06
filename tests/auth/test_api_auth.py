from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.auth import get_current_user, get_current_user_id
from app.domain.models import User


@pytest.mark.asyncio
async def test_get_current_user_id_returns_subject() -> None:
    user_id = uuid4()

    with patch(
        "app.api.auth.decode_access_token",
        return_value=str(user_id),
    ):
        result = await get_current_user_id("valid-token")

    assert result == user_id


@pytest.mark.asyncio
async def test_get_current_user_id_rejects_invalid_token() -> None:
    from app.application.auth.tokens import InvalidTokenError

    with patch(
        "app.api.auth.decode_access_token",
        side_effect=InvalidTokenError("invalid"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id("invalid-token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_get_current_user_id_rejects_invalid_uuid() -> None:
    with patch(
        "app.api.auth.decode_access_token",
        return_value="not-a-uuid",
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id("valid-token")

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_returns_active_user() -> None:
    user_id = uuid4()

    user = User(
        id=user_id,
        email="user@nexusai.test",
        password_hash="hashed-password",
        role="user",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repository = AsyncMock()
    repository.get_by_id.return_value = user

    result = await get_current_user(
        user_id=user_id,
        repository=repository,
    )

    assert result == user
    repository.get_by_id.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_get_current_user_rejects_missing_user() -> None:
    user_id = uuid4()

    repository = AsyncMock()
    repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            user_id=user_id,
            repository=repository,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_inactive_user() -> None:
    user_id = uuid4()

    user = User(
        id=user_id,
        email="inactive@nexusai.test",
        password_hash="hashed-password",
        role="user",
        is_active=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repository = AsyncMock()
    repository.get_by_id.return_value = user

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            user_id=user_id,
            repository=repository,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_require_role_allows_matching_role() -> None:
    from app.api.auth import require_role

    user_id = uuid4()

    user = User(
        id=user_id,
        email="admin@nexusai.test",
        password_hash="hashed-password",
        role="admin",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    dependency = require_role("admin")

    result = await dependency(current_user=user)

    assert result == user


@pytest.mark.asyncio
async def test_require_role_rejects_wrong_role() -> None:
    from app.api.auth import require_role

    user_id = uuid4()

    user = User(
        id=user_id,
        email="user@nexusai.test",
        password_hash="hashed-password",
        role="user",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    dependency = require_role("admin")

    with pytest.raises(HTTPException) as exc_info:
        await dependency(current_user=user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient permissions"


@pytest.mark.asyncio
async def test_require_role_allows_multiple_roles() -> None:
    from app.api.auth import require_role

    user_id = uuid4()

    user = User(
        id=user_id,
        email="user@nexusai.test",
        password_hash="hashed-password",
        role="user",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    dependency = require_role("user", "admin")

    result = await dependency(current_user=user)

    assert result == user


@pytest.mark.asyncio
async def test_get_current_user_rejects_inactive_user_with_valid_user_id() -> None:
    user_id = uuid4()

    user = User(
        id=user_id,
        email="revoked@nexusai.test",
        password_hash="hashed-password",
        role="user",
        is_active=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repository = AsyncMock()
    repository.get_by_id.return_value = user

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            user_id=user_id,
            repository=repository,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"

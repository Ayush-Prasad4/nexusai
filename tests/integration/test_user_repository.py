import asyncio
from datetime import datetime, timezone

from sqlalchemy import delete

from app.domain.models import User
from app.infrastructure.database.models import UserModel
from app.infrastructure.database.session import AsyncSessionFactory, engine
from app.infrastructure.repositories.postgres import PostgresUserRepository


def test_user_repository_persistence() -> None:
    asyncio.run(_test_user_repository_persistence())


async def _test_user_repository_persistence() -> None:
    repository = PostgresUserRepository(AsyncSessionFactory)

    now = datetime.now(timezone.utc)

    user = User(
        email="integration@nexusai.test",
        password_hash="hashed-password",
        role="user",
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    saved = await repository.create(user)

    try:
        loaded_by_id = await repository.get_by_id(saved.id)
        loaded_by_email = await repository.get_by_email(saved.email)

        assert loaded_by_id is not None
        assert loaded_by_email is not None

        assert loaded_by_id.id == saved.id
        assert loaded_by_id.email == saved.email
        assert loaded_by_id.password_hash == saved.password_hash
        assert loaded_by_id.role == saved.role
        assert loaded_by_id.is_active == saved.is_active
        assert loaded_by_id.created_at == saved.created_at
        assert loaded_by_id.updated_at == saved.updated_at

        assert loaded_by_email.id == saved.id

    finally:
        async with AsyncSessionFactory() as session:
            await session.execute(
                delete(UserModel).where(
                    UserModel.id == saved.id
                )
            )
            await session.commit()

        await engine.dispose()


def test_registration_service_with_postgres() -> None:
    asyncio.run(_test_registration_service_with_postgres())


async def _test_registration_service_with_postgres() -> None:
    from app.application.auth.registration import RegistrationService

    repository = PostgresUserRepository(AsyncSessionFactory)
    service = RegistrationService(repository)

    user = await service.register(
        email="registration@nexusai.test",
        password="secure-password",
    )

    try:
        loaded = await repository.get_by_email(
            "registration@nexusai.test"
        )

        assert loaded is not None
        assert loaded.id == user.id
        assert loaded.email == user.email
        assert loaded.password_hash != "secure-password"
        assert loaded.password_hash.startswith("$argon2")
        assert loaded.role == "user"
        assert loaded.is_active is True

    finally:
        async with AsyncSessionFactory() as session:
            await session.execute(
                delete(UserModel).where(
                    UserModel.id == user.id
                )
            )
            await session.commit()

        await engine.dispose()


def test_login_service_with_postgres() -> None:
    asyncio.run(_test_login_service_with_postgres())


async def _test_login_service_with_postgres() -> None:
    from app.application.auth.login import LoginService
    from app.application.auth.registration import RegistrationService
    from app.application.auth.tokens import decode_access_token

    repository = PostgresUserRepository(AsyncSessionFactory)

    registration_service = RegistrationService(repository)
    login_service = LoginService(repository)

    user = await registration_service.register(
        email="login@nexusai.test",
        password="secure-password",
    )

    try:
        access_token = await login_service.login(
            email="login@nexusai.test",
            password="secure-password",
        )

        subject = decode_access_token(access_token)

        assert subject == str(user.id)

    finally:
        async with AsyncSessionFactory() as session:
            await session.execute(
                delete(UserModel).where(
                    UserModel.id == user.id
                )
            )
            await session.commit()

        await engine.dispose()

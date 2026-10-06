import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_development_environment_is_valid() -> None:
    settings = Settings(
        jwt_secret_key="test-secret-that-is-at-least-32-chars",
        environment="development",
    )

    assert settings.environment == "development"


def test_testing_environment_is_valid() -> None:
    settings = Settings(
        jwt_secret_key="test-secret-that-is-at-least-32-chars",
        environment="testing",
    )

    assert settings.environment == "testing"


def test_production_environment_is_valid() -> None:
    settings = Settings(
        jwt_secret_key="test-secret-that-is-at-least-32-chars",
        environment="production",
    )

    assert settings.environment == "production"


def test_unknown_environment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(
            jwt_secret_key="test-secret-that-is-at-least-32-chars",
            environment="staging",
        )

def test_short_jwt_secret_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(
            jwt_secret_key="too-short",
            environment="development",
        )

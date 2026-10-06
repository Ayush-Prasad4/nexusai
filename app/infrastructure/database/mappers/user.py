from app.domain.models import User
from app.infrastructure.database.models import UserModel


def to_model(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        email=user.email,
        password_hash=user.password_hash,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        password_hash=model.password_hash,
        role=model.role,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.auth import get_current_user
from app.api.dependencies import get_user_repository
from app.api.v1.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.application.auth.login import (
    AuthenticationError,
    LoginService,
)
from app.application.auth.registration import RegistrationService
from app.domain.repositories import UserRepository


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: UserRegisterRequest,
    repository: UserRepository = Depends(get_user_repository),
) -> UserResponse:
    service = RegistrationService(repository)

    try:
        user = await service.register(
            email=request.email,
            password=request.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )



@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    request: UserLoginRequest,
    repository: UserRepository = Depends(get_user_repository),
) -> TokenResponse:
    service = LoginService(repository)

    try:
        access_token = await service.login(
            email=request.email,
            password=request.password,
        )
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return TokenResponse(
        access_token=access_token,
    )


@router.get("/me")
async def get_me(
    current_user: Annotated[str, Depends(get_current_user)],
) -> dict[str, str]:
    return {"user_id": current_user}

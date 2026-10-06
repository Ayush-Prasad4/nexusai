from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.auth import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def get_me(
    current_user: Annotated[str, Depends(get_current_user)],
) -> dict[str, str]:
    return {"user_id": current_user}

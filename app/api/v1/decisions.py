from datetime import datetime, timezone

from fastapi import APIRouter, status

from app.domain.models import DecisionRequest, DecisionRun

router = APIRouter(tags=["decisions"])


@router.post(
    "/decisions",
    status_code=status.HTTP_201_CREATED,
)
async def create_decision(
    request: DecisionRequest,
) -> DecisionRun:
    now = datetime.now(timezone.utc)

    return DecisionRun(
        created_at=now,
        updated_at=now,
    )

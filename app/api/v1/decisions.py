from datetime import datetime, timezone

from fastapi import APIRouter, status

from app.api.v1.schemas import DecisionRunResponse
from app.domain.models import DecisionRequest, DecisionRun

router = APIRouter(tags=["decisions"])


@router.post(
    "/decisions",
    response_model=DecisionRunResponse,
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

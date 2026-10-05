from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_decision_job_queue,
    get_decision_repository,
)
from app.api.v1.schemas import DecisionRunResponse
from app.application.decision_service import DecisionService
from app.domain.models import DecisionRequest
from app.domain.repositories import DecisionRunRepository
from app.infrastructure.redis.queue import DecisionJobQueue

router = APIRouter(tags=["decisions"])


@router.post(
    "/decisions",
    response_model=DecisionRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_decision(
    request: DecisionRequest,
    repository: DecisionRunRepository = Depends(get_decision_repository),
    job_queue: DecisionJobQueue = Depends(get_decision_job_queue),
) -> DecisionRunResponse:
    service = DecisionService(repository, job_queue)

    run = await service.create_decision(request)

    return DecisionRunResponse(
        id=run.id,
        status=run.status,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )

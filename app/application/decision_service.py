from datetime import datetime, timezone

from app.domain.models import DecisionRequest, DecisionRun
from app.domain.repositories import DecisionRunRepository


class DecisionService:
    def __init__(self, repository: DecisionRunRepository) -> None:
        self.repository = repository

    async def create_decision(
        self,
        request: DecisionRequest,
    ) -> DecisionRun:
        now = datetime.now(timezone.utc)

        run = DecisionRun(
            objective=request.objective,
            context=request.context,
            created_at=now,
            updated_at=now,
        )

        return await self.repository.save(run)

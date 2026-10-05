from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.status import DecisionRunStatus


class DecisionRunResponse(BaseModel):
    id: UUID
    status: DecisionRunStatus
    created_at: datetime
    updated_at: datetime

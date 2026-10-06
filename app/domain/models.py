from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.status import DecisionRunStatus


class DecisionRequest(BaseModel):
    objective: str = Field(min_length=1, max_length=10_000)
    context: str | None = Field(default=None, max_length=50_000)


class DecisionRun(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: DecisionRunStatus = DecisionRunStatus.PENDING
    objective: str
    context: str | None = None
    created_at: datetime
    updated_at: datetime


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: str
    password_hash: str
    role: str = "user"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

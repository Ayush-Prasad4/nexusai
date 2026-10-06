from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.status import DecisionRunStatus


class DecisionRunResponse(BaseModel):
    id: UUID
    status: DecisionRunStatus
    created_at: datetime
    updated_at: datetime


class UserRegisterRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

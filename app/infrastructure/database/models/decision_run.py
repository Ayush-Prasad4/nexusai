from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.status import DecisionRunStatus
from app.infrastructure.database.base import Base


class DecisionRunModel(Base):
    __tablename__ = "decision_runs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=DecisionRunStatus.PENDING.value,
    )

    objective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

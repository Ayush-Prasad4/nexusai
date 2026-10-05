from datetime import datetime, timezone
from uuid import UUID

from pydantic import ValidationError

from app.domain.models import DecisionRequest, DecisionRun
from app.domain.status import DecisionRunStatus


def test_decision_run_defaults() -> None:
    now = datetime.now(timezone.utc)

    run = DecisionRun(
        created_at=now,
        updated_at=now,
    )

    assert isinstance(run.id, UUID)
    assert run.status == DecisionRunStatus.PENDING
    assert run.created_at == now
    assert run.updated_at == now


def test_decision_request() -> None:
    request = DecisionRequest(
        objective="Assess whether this supplier should be retained.",
        context="Supplier has experienced repeated delivery delays.",
    )

    assert request.objective.startswith("Assess")
    assert request.context is not None


def test_decision_request_requires_objective() -> None:
    try:
        DecisionRequest(objective="")
    except ValidationError:
        return

    raise AssertionError("Expected validation error")

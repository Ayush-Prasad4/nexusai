from app.domain.models import DecisionRun
from app.domain.status import DecisionRunStatus
from app.infrastructure.database.models import DecisionRunModel


def to_domain(model: DecisionRunModel) -> DecisionRun:
    return DecisionRun(
        id=model.id,
        status=DecisionRunStatus(model.status),
        objective=model.objective,
        context=model.context,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_model(run: DecisionRun) -> DecisionRunModel:
    return DecisionRunModel(
        id=run.id,
        status=run.status.value,
        objective=run.objective,
        context=run.context,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )

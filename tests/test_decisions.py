import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_decision_job_queue,
    get_decision_repository,
)
from app.domain.models import DecisionRun
from app.main import app


class FakeDecisionRunRepository:
    def __init__(self) -> None:
        self.runs: dict = {}

    async def save(self, run: DecisionRun) -> DecisionRun:
        self.runs[run.id] = run
        return run

    async def get(self, run_id):
        return self.runs.get(run_id)


class FakeDecisionJobQueue:
    def __init__(self) -> None:
        self.jobs = []

    async def enqueue(self, job) -> None:
        self.jobs.append(job)


@pytest.fixture
def client() -> TestClient:
    fake_repository = FakeDecisionRunRepository()
    fake_job_queue = FakeDecisionJobQueue()

    app.dependency_overrides[get_decision_repository] = (
        lambda: fake_repository
    )
    app.dependency_overrides[get_decision_job_queue] = (
        lambda: fake_job_queue
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_decision_repository, None)
    app.dependency_overrides.pop(get_decision_job_queue, None)


def test_create_decision(client: TestClient) -> None:
    response = client.post(
        "/v1/decisions",
        json={
            "objective": "Assess whether this supplier should be retained.",
            "context": "Supplier has experienced repeated delivery delays.",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body
    assert body["status"] == "pending"
    assert "created_at" in body
    assert "updated_at" in body


def test_create_decision_requires_objective(client: TestClient) -> None:
    response = client.post(
        "/v1/decisions",
        json={
            "objective": "",
        },
    )

    assert response.status_code == 422


def test_create_decision_response_contract(client: TestClient) -> None:
    response = client.post(
        "/v1/decisions",
        json={
            "objective": "Evaluate a business decision.",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert set(body.keys()) == {
        "id",
        "status",
        "created_at",
        "updated_at",
    }
    assert body["status"] == "pending"

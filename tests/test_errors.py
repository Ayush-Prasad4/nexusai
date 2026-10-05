from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.core.errors.exceptions import NexusAIException
from app.main import app


router = APIRouter()


@router.get("/test-error")
async def trigger_test_error() -> None:
    raise NexusAIException(
        code="TEST_ERROR",
        message="This is a test error.",
    )


app.include_router(router)

client = TestClient(app)


def test_nexusai_exception_handler() -> None:
    response = client.get("/test-error")

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "TEST_ERROR",
            "message": "This is a test error.",
        }
    }

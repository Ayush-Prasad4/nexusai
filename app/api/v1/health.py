from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.infrastructure.database.session import engine


router = APIRouter(tags=["health"])


@router.get("/health/live")
async def liveness_check() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/health/ready", response_model=None)
async def readiness_check(request: Request) -> dict[str, str] | JSONResponse:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        redis = getattr(request.app.state, "redis", None)

        if redis is None:
            raise RuntimeError("Redis client is not initialized")

        await redis.ping()

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready"},
        )

    return {"status": "ready"}

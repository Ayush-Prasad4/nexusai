from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health/live")
async def liveness_check() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_check() -> dict[str, str]:
    return {"status": "ready"}

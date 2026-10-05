from fastapi import APIRouter

from app.api.v1.decisions import router as decisions_router
from app.api.v1.health import router as health_router


api_router = APIRouter(prefix="/v1")

api_router.include_router(health_router)
api_router.include_router(decisions_router)

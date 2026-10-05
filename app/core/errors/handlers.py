from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.errors.exceptions import NexusAIException


async def nexusai_exception_handler(
    request: Request,
    exc: NexusAIException,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )

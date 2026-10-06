import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.errors.exceptions import NexusAIException

logger = logging.getLogger(__name__)


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


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "unhandled_exception method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An internal server error occurred.",
            }
        },
    )

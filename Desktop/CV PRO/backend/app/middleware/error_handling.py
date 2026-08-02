"""Global Error Handling Middleware"""

from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """Catch and format all exceptions."""

    try:
        response = await call_next(request)
        return response
    except Exception as e:
        # Log error
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)

        # Return formatted error response
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal Server Error",
                "type": type(e).__name__,
                "message": str(e) if hasattr(e, '__str__') else "Unknown error",
            },
        )

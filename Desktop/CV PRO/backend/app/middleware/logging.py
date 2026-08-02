"""Request Logging Middleware"""

import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next):
    """Log all HTTP requests and responses."""

    # Skip logging for health checks
    if request.url.path in ["/health", "/readiness"]:
        return await call_next(request)

    start_time = time.time()

    # Get request info
    method = request.method
    path = request.url.path
    query_string = request.url.query

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log structured
    log_data = {
        "method": method,
        "path": path,
        "query": query_string if query_string else None,
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
        "timestamp": time.time(),
    }

    logger.info(json.dumps(log_data))

    # Add response headers
    response.headers["X-Process-Time"] = str(duration)

    return response

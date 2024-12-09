# middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses.
    """
    async def dispatch(self, request: Request, call_next):
        # Log before processing the request
        logger.info(f"Before Request: {request.method} {request.url}")
        # Process the request
        response = await call_next(request)
        # Log after processing the request
        logger.info(f"After Request: {request.method} {request.url} - Status: {response.status_code}")
        return response

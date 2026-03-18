"""Custom exceptions and FastAPI exception handlers for CloudAdvisor."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class CloudAdvisorError(Exception):
    """Base exception for CloudAdvisor."""


class ClaudeAPIError(CloudAdvisorError):
    """Raised when the Anthropic API returns an error response."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ClaudeRateLimitError(CloudAdvisorError):
    """Raised when the Anthropic API rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded. Please try again shortly.") -> None:
        self.message = message
        super().__init__(message)


class ValidationError(CloudAdvisorError):
    """Raised for custom business-logic validation failures."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI application.

    Args:
        app: The FastAPI application instance to register handlers on.
    """

    @app.exception_handler(ClaudeAPIError)
    async def claude_api_error_handler(request: Request, exc: ClaudeAPIError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "type": "claude_api_error"},
        )

    @app.exception_handler(ClaudeRateLimitError)
    async def claude_rate_limit_handler(request: Request, exc: ClaudeRateLimitError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"error": exc.message, "type": "rate_limit_error"},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": exc.message, "type": "validation_error"},
        )
"""CloudAdvisor FastAPI application factory.

Wires together configuration, middleware, routers, services, and exception
handlers. Use `create_app()` to build the application — this pattern makes
the app fully testable by allowing dependency injection overrides.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.exceptions import register_exception_handlers
from app.routers import health, history, query
from app.services.claude_service import ClaudeService
from app.services.history_service import HistoryService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Application factory — builds and configures the FastAPI instance.

    Returns:
        A fully configured FastAPI application.
    """
    settings = get_settings()

    # Shared service singletons
    claude_service = ClaudeService(settings)
    history_service = HistoryService()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Manage application lifespan events.

        Startup: log service readiness.
        Shutdown: (no-op for in-memory store — add cleanup here for real DBs).
        """
        logger.info(
            "CloudAdvisor starting — model=%s, debug=%s",
            settings.model_name,
            settings.debug,
        )
        yield
        logger.info("CloudAdvisor shutting down")

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "AI-powered Cloud & IT Solutions Q&A assistant. "
            "Ask questions about cloud migration, Google Workspace, security, and more."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS — allow the configured frontend origins
    origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Wire dependency overrides so routers receive real service instances
    app.dependency_overrides[query.get_claude_service] = lambda: claude_service
    app.dependency_overrides[query.get_history_service] = lambda: history_service
    app.dependency_overrides[history.get_history_service] = lambda: history_service

    # Register routers
    app.include_router(query.router, prefix="/api")
    app.include_router(history.router, prefix="/api")
    app.include_router(health.router, prefix="/api")

    # Register custom exception handlers
    register_exception_handlers(app)

    return app


app = create_app()
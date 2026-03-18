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
from app.services.cache_service import CacheService
from app.services.claude_service import ClaudeService
from app.services.database import close_db, get_db_session, init_db
from app.services.history_service import HistoryService
from app.services.validation_service import ResponseValidationService

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
    validation_service = ResponseValidationService()
    cache_service = CacheService(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Manage application lifespan events.

        Startup: initialise database, Redis, and log readiness.
        Shutdown: close database and Redis connections.
        """
        await init_db()
        await cache_service.connect()
        logger.info(
            "CloudAdvisor starting — model=%s, debug=%s, db=connected, redis=%s",
            settings.model_name,
            settings.debug,
            "connected" if cache_service.is_connected else "unavailable",
        )
        yield
        await cache_service.disconnect()
        await close_db()
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
    async def _get_history_service():
        async for session in get_db_session():
            yield HistoryService(session)

    app.dependency_overrides[query.get_claude_service] = lambda: claude_service
    app.dependency_overrides[query.get_validation_service] = lambda: validation_service
    app.dependency_overrides[query.get_cache_service] = lambda: cache_service
    app.dependency_overrides[query.get_history_service] = _get_history_service
    app.dependency_overrides[history.get_history_service] = _get_history_service

    # Register routers
    app.include_router(query.router, prefix="/api")
    app.include_router(history.router, prefix="/api")
    app.include_router(health.router, prefix="/api")

    # Register custom exception handlers
    register_exception_handlers(app)

    return app


app = create_app()
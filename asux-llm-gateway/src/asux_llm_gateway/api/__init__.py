from fastapi import FastAPI

from asux_llm_gateway.api.routes import router
from asux_llm_gateway.observability.logging import get_logger
from asux_llm_gateway.providers.registry import registry

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.
    """
    app = FastAPI(
        title="AsuX LLM Gateway",
        description="Production-oriented, provider-independent LLM Gateway V1",
        version="1.0.0",
    )

    @app.on_event("startup")
    async def startup_event() -> None:
        logger.info("Initializing LLM Gateway API...")
        registry.initialize_defaults()
        logger.info("LLM Gateway API started successfully.")

    app.include_router(router)

    return app

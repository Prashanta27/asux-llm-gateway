import uvicorn

from asux_llm_gateway.config import settings


def main() -> None:
    """Entry point for the CLI."""
    uvicorn.run(
        "asux_llm_gateway.api:create_app",
        host=settings.api_host,
        port=settings.api_port,
        factory=True,
        reload=(settings.environment == "development"),
    )


if __name__ == "__main__":
    main()

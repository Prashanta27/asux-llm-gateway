from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration for the LLM Gateway.
    Loads from environment variables or a .env file.
    """

    # Environment
    environment: str = Field(
        default="development", description="Environment (development, staging, production)"
    )

    # API Settings
    api_host: str = Field(default="0.0.0.0", description="Host to bind the API to")
    api_port: int = Field(default=8000, description="Port to bind the API to")

    # Default Provider Settings
    default_provider: str = Field(
        default="openai", description="Default provider if none specified"
    )
    default_model: str = Field(default="gpt-4o-mini", description="Default model if none specified")

    # Provider API Keys
    openai_api_key: str | None = Field(default=None, description="OpenAI API Key")
    openai_base_url: str | None = Field(default=None, description="OpenAI Base URL override")

    # Timeout Settings
    request_timeout: float = Field(default=60.0, description="Default request timeout in seconds")
    connect_timeout: float = Field(default=10.0, description="Default connect timeout in seconds")

    # Retry Settings
    retry_count: int = Field(default=3, description="Default number of retries")
    retry_backoff_factor: float = Field(default=2.0, description="Exponential backoff factor")
    retry_max_delay: float = Field(
        default=10.0, description="Maximum delay between retries in seconds"
    )

    # Observability
    log_level: str = Field(
        default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_prompts: bool = Field(
        default=False, description="Whether to log full prompts (disable in production)"
    )

    # Cost tracking
    enable_cost_tracking: bool = Field(
        default=True, description="Whether to calculate and log estimated costs"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Global settings instance
settings = Settings()

from asux_llm_gateway.config import settings
from asux_llm_gateway.exceptions.errors import ConfigurationError
from asux_llm_gateway.providers.base import BaseLLMProvider
from asux_llm_gateway.providers.openai_compatible import OpenAICompatibleProvider


class ProviderRegistry:
    """
    Manages available LLM providers.
    """

    def __init__(self) -> None:
        self._providers: dict[str, BaseLLMProvider] = {}

    def register(self, name: str, provider: BaseLLMProvider) -> None:
        self._providers[name] = provider

    def get(self, name: str) -> BaseLLMProvider:
        if name not in self._providers:
            raise ConfigurationError(f"Provider '{name}' not found in registry.")
        return self._providers[name]

    def initialize_defaults(self) -> None:
        """
        Initializes providers based on environment configuration.
        """
        if settings.openai_api_key:
            self.register(
                "openai",
                OpenAICompatibleProvider(
                    api_key=settings.openai_api_key,
                    base_url=settings.openai_base_url or "https://api.openai.com/v1",
                ),
            )


# Global registry instance
registry = ProviderRegistry()

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from asux_llm_gateway.models.requests import GatewayRequest
from asux_llm_gateway.models.responses import GatewayResponse, StreamChunk


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    All providers must implement these methods.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the name of the provider (e.g., 'openai')."""
        pass

    @abstractmethod
    async def complete(self, request: GatewayRequest, request_id: str) -> GatewayResponse:
        """
        Executes a standard, non-streaming completion request.
        """
        pass

    @abstractmethod
    def stream(self, request: GatewayRequest, request_id: str) -> AsyncGenerator[StreamChunk, None]:
        """
        Executes a streaming completion request.
        """
        pass

from typing import Any

from pydantic import BaseModel, Field

from asux_llm_gateway.models.messages import Message
from asux_llm_gateway.models.usage import TokenUsage


class GatewayResponse(BaseModel):
    """
    Standardized response format from the LLM Gateway.
    """

    request_id: str = Field(..., description="Unique identifier for the request.")
    model: str = Field(..., description="The actual model used to generate the response.")
    provider: str = Field(..., description="The provider that fulfilled the request.")

    # Core Response Data
    message: Message = Field(..., description="The assistant's response message.")
    finish_reason: str | None = Field(
        default=None,
        description="Reason the model stopped generating (e.g., 'stop', 'length', 'tool_calls').",
    )

    # Observability
    usage: TokenUsage | None = Field(default=None, description="Token usage statistics.")
    latency_ms: float | None = Field(default=None, description="Request latency in milliseconds.")
    estimated_cost: float | None = Field(default=None, description="Estimated cost in USD.")

    # Provider-specific extras
    provider_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Any extra provider-specific response data."
    )

    @property
    def content(self) -> str:
        """Helper to get text content directly."""
        return self.message.content or ""


class StreamChunk(BaseModel):
    """
    Standardized chunk format for streaming responses.
    """

    request_id: str
    model: str
    provider: str

    # Delta content
    content_delta: str = Field(default="")

    finish_reason: str | None = None
    usage: TokenUsage | None = None

    # We might have tool call deltas in the future, but for V1 we focus on text.

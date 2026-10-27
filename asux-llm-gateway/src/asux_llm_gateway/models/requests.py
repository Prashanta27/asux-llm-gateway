from typing import Any

from pydantic import BaseModel, Field

from asux_llm_gateway.models.messages import Message


class GatewayRequest(BaseModel):
    """
    Standardized request format for the LLM Gateway.
    """

    # Routing and Model Selection
    model: str | None = Field(
        default=None, description="The model to use. If None, the router will select the default."
    )
    provider: str | None = Field(
        default=None,
        description="Explicitly request a specific provider. Usually left to the router.",
    )

    # Core LLM Parameters
    messages: list[Message] = Field(..., description="The conversation history.")
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)

    # Execution Modifiers
    stream: bool = Field(default=False, description="Whether to stream the response.")

    # Structured Output
    # This is handled separately in the client for type safety, but the gateway
    # may need to pass schema information to the provider.
    response_format: dict[str, Any] | None = Field(
        default=None, description="Format specification (e.g., JSON schema for structured output)."
    )

    # Tools
    tools: list[dict[str, Any]] | None = Field(
        default=None, description="List of tools the model can call."
    )

    # Gateway Overrides
    timeout: float | None = Field(default=None, description="Request timeout override.")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Custom metadata for observability/tracking."
    )

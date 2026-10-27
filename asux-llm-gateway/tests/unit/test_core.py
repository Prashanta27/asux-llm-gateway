from collections.abc import AsyncGenerator

import pytest
from pydantic import BaseModel

from asux_llm_gateway.clients.llm_client import LLMClient
from asux_llm_gateway.cost.tracker import CostTracker
from asux_llm_gateway.exceptions.errors import AuthenticationError, ProviderError
from asux_llm_gateway.models.messages import Message
from asux_llm_gateway.models.requests import GatewayRequest
from asux_llm_gateway.models.responses import GatewayResponse, StreamChunk
from asux_llm_gateway.models.usage import TokenUsage
from asux_llm_gateway.providers.base import BaseLLMProvider
from asux_llm_gateway.retry.policy import RetryPolicy


def test_token_usage_addition():
    u1 = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    u2 = TokenUsage(prompt_tokens=5, completion_tokens=None, total_tokens=5)

    u3 = u1.add(u2)
    assert u3.prompt_tokens == 15
    assert u3.completion_tokens == 20
    assert u3.total_tokens == 35


def test_cost_tracker_calculation():
    # gpt-4o-mini is 0.00015 per 1k prompt, 0.0006 per 1k completion
    usage = TokenUsage(prompt_tokens=1000, completion_tokens=2000, total_tokens=3000)
    cost = CostTracker.calculate_cost("gpt-4o-mini", usage)

    # 1 * 0.00015 + 2 * 0.0006 = 0.00015 + 0.0012 = 0.00135
    assert cost is not None
    assert abs(cost - 0.00135) < 1e-6


def test_cost_tracker_unknown_model():
    usage = TokenUsage(prompt_tokens=1000, completion_tokens=1000)
    cost = CostTracker.calculate_cost("unknown-model", usage)
    assert cost is None


def test_retry_policy_should_retry():
    assert RetryPolicy.should_retry(ProviderError("502 Bad Gateway"))
    assert not RetryPolicy.should_retry(AuthenticationError("Invalid API key"))


class SimpleMockProvider(BaseLLMProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    async def stream(self, req, rid) -> AsyncGenerator[StreamChunk, None]:
        yield StreamChunk(request_id=rid, model="mock", provider="mock", content_delta="test")

    async def complete(self, req, rid) -> GatewayResponse:
        return GatewayResponse(
            request_id=rid,
            model="mock",
            provider=self.provider_name,
            message=Message.assistant(content="Mock response"),
        )


@pytest.mark.asyncio
async def test_llm_client_complete():
    from asux_llm_gateway.providers.registry import registry

    registry.register("mock", SimpleMockProvider())
    from asux_llm_gateway.config import settings

    settings.default_provider = "mock"

    client = LLMClient()
    request = GatewayRequest(messages=[Message.user("Hello")])
    response = await client.complete(request)

    assert response.provider == "mock"
    assert response.content == "Mock response"


@pytest.mark.asyncio
async def test_llm_client_structured():
    import json

    from asux_llm_gateway.providers.registry import registry

    class FakeStructProvider(BaseLLMProvider):
        @property
        def provider_name(self) -> str:
            return "fake"

        async def stream(self, req, rid) -> AsyncGenerator[StreamChunk, None]:
            yield StreamChunk(request_id=rid, model="fake", provider="fake", content_delta="")

        async def complete(self, req, rid) -> GatewayResponse:
            return GatewayResponse(
                request_id=rid,
                model="fake-model",
                provider=self.provider_name,
                message=Message.assistant(content=json.dumps({"name": "Test", "age": 25})),
            )

    registry.register("mock", FakeStructProvider())
    from asux_llm_gateway.config import settings

    settings.default_provider = "mock"

    client = LLMClient()

    class UserSchema(BaseModel):
        name: str
        age: int

    request = GatewayRequest(messages=[Message.user("Get user")])
    result = await client.complete_structured(request, UserSchema)

    assert isinstance(result, UserSchema)
    assert result.name == "Test"
    assert result.age == 25

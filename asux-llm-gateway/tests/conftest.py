import os
from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from asux_llm_gateway.api import create_app
from asux_llm_gateway.config import settings
from asux_llm_gateway.models.messages import Message
from asux_llm_gateway.models.requests import GatewayRequest
from asux_llm_gateway.models.responses import GatewayResponse, StreamChunk
from asux_llm_gateway.models.usage import TokenUsage
from asux_llm_gateway.providers.base import BaseLLMProvider
from asux_llm_gateway.providers.registry import registry

os.environ["ENVIRONMENT"] = "testing"
os.environ["ENABLE_COST_TRACKING"] = "1"
os.environ["OPENAI_API_KEY"] = "fake-api-key"


class MockProvider(BaseLLMProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    async def complete(self, request: GatewayRequest, request_id: str) -> GatewayResponse:
        return GatewayResponse(
            request_id=request_id,
            model=request.model or "mock-model",
            provider=self.provider_name,
            message=Message.assistant(content="Mock response"),
            finish_reason="stop",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            latency_ms=10.0,
        )

    async def stream(
        self, request: GatewayRequest, request_id: str
    ) -> AsyncGenerator[StreamChunk, None]:
        chunks = ["Mock ", "streaming ", "response"]
        for c in chunks:
            yield StreamChunk(
                request_id=request_id,
                model=request.model or "mock-model",
                provider=self.provider_name,
                content_delta=c,
            )
        yield StreamChunk(
            request_id=request_id,
            model=request.model or "mock-model",
            provider=self.provider_name,
            finish_reason="stop",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        )


@pytest.fixture
def app() -> FastAPI:
    app_instance = create_app()
    registry.register("mock", MockProvider())
    settings.default_provider = "mock"
    return app_instance


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as c:
        yield c

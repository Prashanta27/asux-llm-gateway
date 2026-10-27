import json
import time
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from asux_llm_gateway.config import settings
from asux_llm_gateway.exceptions.errors import (
    AuthenticationError,
    InvalidRequestError,
    ProviderError,
    RateLimitError,
    GatewayTimeoutError,
)
from asux_llm_gateway.models.messages import Message, MessageRole
from asux_llm_gateway.models.requests import GatewayRequest
from asux_llm_gateway.models.responses import GatewayResponse, StreamChunk
from asux_llm_gateway.models.usage import TokenUsage
from asux_llm_gateway.observability.logging import get_logger
from asux_llm_gateway.providers.base import BaseLLMProvider

logger = get_logger(__name__)


class OpenAICompatibleProvider(BaseLLMProvider):
    """
    Provider implementation that uses the OpenAI-compatible HTTP API.
    Handles communication with OpenAI, local models (vLLM, Ollama via proxy), etc.
    """

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        # Default to OpenAI URL if none provided, though often overridden
        self.base_url = base_url.rstrip("/") if base_url else "https://api.openai.com/v1"

        # Setup httpx client
        timeout = httpx.Timeout(settings.request_timeout, connect=settings.connect_timeout)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=timeout,
        )

    @property
    def provider_name(self) -> str:
        # Assuming if we use openai base url it's openai, else custom
        if "api.openai.com" in self.base_url:
            return "openai"
        return "openai-compatible"

    def _map_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        mapped = []
        for msg in messages:
            m = {"role": msg.role.value, "content": msg.content or ""}
            # For v1 we focus on basic roles. Tool calls would be mapped here.
            mapped.append(m)
        return mapped

    def _prepare_payload(self, request: GatewayRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": self._map_messages(request.messages),
            "stream": request.stream,
        }

        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.response_format:
            payload["response_format"] = request.response_format

        return payload

    def _handle_http_error(self, response: httpx.Response) -> None:
        if response.is_success:
            return

        status = response.status_code
        try:
            error_data = response.json()
            err_msg = error_data.get("error", {}).get("message", response.text)
        except Exception:
            err_msg = response.text

        if status == 401:
            raise AuthenticationError(f"Authentication failed: {err_msg}")
        elif status == 429:
            raise RateLimitError(f"Rate limit exceeded: {err_msg}")
        elif status in (400, 404, 422):
            raise InvalidRequestError(f"Invalid request: {err_msg}")
        else:
            raise ProviderError(f"Provider returned {status}: {err_msg}")

    async def complete(self, request: GatewayRequest, request_id: str) -> GatewayResponse:
        start_time = time.monotonic()
        payload = self._prepare_payload(request)

        try:
            response = await self.client.post("/chat/completions", json=payload)
            self._handle_http_error(response)

            data = response.json()
            latency = (time.monotonic() - start_time) * 1000

            choice = data["choices"][0]
            msg_data = choice["message"]

            usage_data = data.get("usage", {})
            usage = TokenUsage(
                prompt_tokens=usage_data.get("prompt_tokens"),
                completion_tokens=usage_data.get("completion_tokens"),
                total_tokens=usage_data.get("total_tokens"),
            )

            # Reconstruct our standard Message
            msg = Message(role=MessageRole(msg_data["role"]), content=msg_data.get("content"))

            return GatewayResponse(
                request_id=request_id,
                model=data.get("model", request.model),
                provider=self.provider_name,
                message=msg,
                finish_reason=choice.get("finish_reason"),
                usage=usage,
                latency_ms=latency,
                provider_metadata={"system_fingerprint": data.get("system_fingerprint")},
            )

        except httpx.TimeoutException as e:
            raise GatewayTimeoutError(f"Request to provider timed out: {e!s}")
        except httpx.RequestError as e:
            raise ProviderError(f"Network error communicating with provider: {e!s}")

    async def stream(
        self, request: GatewayRequest, request_id: str
    ) -> AsyncGenerator[StreamChunk, None]:
        payload = self._prepare_payload(request)
        payload["stream"] = True
        payload["stream_options"] = {"include_usage": True}  # Ask for usage in stream

        try:
            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                self._handle_http_error(response)

                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    if line == "data: [DONE]":
                        break
                    if line.startswith("data: "):
                        line_data = line[6:]
                        try:
                            data = json.loads(line_data)

                            # Parse usage if present (usually last chunk)
                            usage = None
                            if data.get("usage"):
                                u_data = data["usage"]
                                usage = TokenUsage(
                                    prompt_tokens=u_data.get("prompt_tokens"),
                                    completion_tokens=u_data.get("completion_tokens"),
                                    total_tokens=u_data.get("total_tokens"),
                                )

                            # Parse content
                            content_delta = ""
                            finish_reason = None
                            if data.get("choices") and len(data["choices"]) > 0:
                                choice = data["choices"][0]
                                delta = choice.get("delta", {})
                                content_delta = delta.get("content", "") or ""
                                finish_reason = choice.get("finish_reason")

                            yield StreamChunk(
                                request_id=request_id,
                                model=data.get("model", request.model or ""),
                                provider=self.provider_name,
                                content_delta=content_delta,
                                finish_reason=finish_reason,
                                usage=usage,
                            )
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to decode stream line: {line_data}")

        except httpx.TimeoutException as e:
            raise GatewayTimeoutError(f"Stream request timed out: {e!s}")
        except httpx.RequestError as e:
            raise ProviderError(f"Stream network error: {e!s}")

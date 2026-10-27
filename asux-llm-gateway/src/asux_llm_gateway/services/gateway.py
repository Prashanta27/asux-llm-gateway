import uuid
from collections.abc import AsyncGenerator

from asux_llm_gateway.cost.tracker import CostTracker
from asux_llm_gateway.models.requests import GatewayRequest
from asux_llm_gateway.models.responses import GatewayResponse, StreamChunk
from asux_llm_gateway.observability.logging import get_logger
from asux_llm_gateway.providers.registry import registry
from asux_llm_gateway.retry.policy import RetryPolicy
from asux_llm_gateway.routing.model_router import ModelRouter

logger = get_logger(__name__)


class GatewayService:
    """
    Core service that orchestrates the flow of a request:
    Request -> Route -> Retry -> Provider -> Cost -> Response
    """

    @staticmethod
    async def complete(request: GatewayRequest) -> GatewayResponse:
        request_id = str(uuid.uuid4())

        provider_name, target_model = ModelRouter.route(request)
        request.model = target_model  # Ensure request has the resolved model

        provider = registry.get(provider_name)

        logger.info(
            "Routing request",
            request_id=request_id,
            provider=provider_name,
            model=target_model,
            metadata=request.metadata,
        )

        # Execute with retry policy
        response = await RetryPolicy.execute_with_retry(provider.complete, request, request_id)

        # Calculate cost if usage is available
        if response.usage:
            cost = CostTracker.calculate_cost(response.model, response.usage)
            response.estimated_cost = cost

        logger.info(
            "Request completed",
            request_id=request_id,
            latency_ms=response.latency_ms,
            usage=response.usage.model_dump() if response.usage else None,
            cost=response.estimated_cost,
        )

        return response

    @staticmethod
    async def stream(request: GatewayRequest) -> AsyncGenerator[StreamChunk, None]:
        request_id = str(uuid.uuid4())

        provider_name, target_model = ModelRouter.route(request)
        request.model = target_model

        provider = registry.get(provider_name)

        logger.info(
            "Routing stream request",
            request_id=request_id,
            provider=provider_name,
            model=target_model,
            metadata=request.metadata,
        )

        # For streams, we only retry the initial connection phase.
        # If the generator starts yielding, and then fails, we don't retry.
        # We wrap the provider.stream call to get the generator safely.

        async def get_stream() -> AsyncGenerator[StreamChunk, None]:
            return provider.stream(request, request_id)

        stream_gen = await RetryPolicy.execute_with_retry(get_stream)

        # Now consume the stream
        total_usage = None
        final_model = target_model

        async for chunk in stream_gen:
            if chunk.usage:
                total_usage = chunk.usage
            if chunk.model:
                final_model = chunk.model
            yield chunk

        # Log completion after stream ends
        cost = None
        if total_usage:
            cost = CostTracker.calculate_cost(final_model, total_usage)

        logger.info(
            "Stream completed",
            request_id=request_id,
            usage=total_usage.model_dump() if total_usage else None,
            cost=cost,
        )

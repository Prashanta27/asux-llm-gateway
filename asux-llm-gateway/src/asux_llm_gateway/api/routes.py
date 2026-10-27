import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from asux_llm_gateway.api.dependencies import get_llm_client
from asux_llm_gateway.clients.llm_client import LLMClient
from asux_llm_gateway.exceptions.errors import (
    AuthenticationError,
    GatewayError,
    InvalidRequestError,
    ProviderError,
    RateLimitError,
    GatewayTimeoutError,
)
from asux_llm_gateway.models.requests import GatewayRequest
from asux_llm_gateway.models.responses import GatewayResponse

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok"}


@router.get("/ready", tags=["System"])
async def readiness_check() -> dict[str, str]:
    """Readiness endpoint. Checks if providers are registered."""
    from asux_llm_gateway.providers.registry import registry

    if not registry._providers:
        raise HTTPException(status_code=503, detail="No providers configured")
    return {"status": "ready"}


@router.post("/v1/chat/completions", response_model=GatewayResponse, tags=["Completions"])
async def create_completion(
    request: GatewayRequest, client: LLMClient = Depends(get_llm_client)
) -> GatewayResponse:
    """
    Standard completion endpoint.
    If streaming is requested, redirects or fails appropriately.
    """
    if request.stream:
        raise HTTPException(
            status_code=400, detail="Use /v1/chat/completions/stream for streaming requests"
        )

    try:
        return await client.complete(request)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except InvalidRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except GatewayTimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except ProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except GatewayError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/chat/completions/stream", tags=["Completions"])
async def create_completion_stream(
    request: GatewayRequest, client: LLMClient = Depends(get_llm_client)
) -> StreamingResponse:
    """
    Streaming completion endpoint. Returns Server-Sent Events (SSE).
    """
    request.stream = True

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in client.stream(request):
                yield f"data: {chunk.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            # If an error happens midway through a stream, we can't change the HTTP status.
            # We can only emit an error event in the stream and close it.
            error_event = {"error": str(e), "type": type(e).__name__}
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

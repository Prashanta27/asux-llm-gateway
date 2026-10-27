import json
from collections.abc import AsyncGenerator
from typing import TypeVar

from pydantic import BaseModel

from asux_llm_gateway.exceptions.errors import StructuredOutputError
from asux_llm_gateway.models.requests import GatewayRequest
from asux_llm_gateway.models.responses import GatewayResponse, StreamChunk
from asux_llm_gateway.services.gateway import GatewayService

TModel = TypeVar("TModel", bound=BaseModel)


class LLMClient:
    """
    Public programmatic interface for the LLM Gateway.
    Future AsuX agents should use this client to interact with models.
    """

    def __init__(self) -> None:
        pass

    async def complete(self, request: GatewayRequest) -> GatewayResponse:
        """
        Executes a standard LLM completion.
        """
        request.stream = False
        return await GatewayService.complete(request)

    async def stream(self, request: GatewayRequest) -> AsyncGenerator[StreamChunk, None]:
        """
        Executes a streaming LLM completion.
        """
        request.stream = True
        async for chunk in GatewayService.stream(request):
            yield chunk

    async def complete_structured(self, request: GatewayRequest, schema: type[TModel]) -> TModel:
        """
        Executes an LLM completion and guarantees the output matches the provided Pydantic schema.
        Uses OpenAI's json_schema response_format approach internally.
        """
        # Inject the schema into the request's response_format
        schema_dict = schema.model_json_schema()

        request.response_format = {
            "type": "json_schema",
            "json_schema": {"name": schema.__name__, "schema": schema_dict, "strict": True},
        }
        request.stream = False

        response = await GatewayService.complete(request)
        content = response.content

        if not content:
            raise StructuredOutputError(
                "Model returned empty content when structured output was expected."
            )

        try:
            # Parse the JSON and validate against the Pydantic schema
            data = json.loads(content)
            return schema.model_validate(data)
        except json.JSONDecodeError as e:
            raise StructuredOutputError(
                f"Model did not return valid JSON: {e!s}\nContent: {content}"
            )
        except Exception as e:
            raise StructuredOutputError(
                f"Model output failed schema validation: {e!s}\nContent: {content}"
            )

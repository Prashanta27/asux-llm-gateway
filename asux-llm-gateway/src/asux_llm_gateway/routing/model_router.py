from asux_llm_gateway.config import settings
from asux_llm_gateway.models.requests import GatewayRequest


class ModelRouter:
    """
    Handles resolving which provider and model to use for a request.
    V1 uses simple deterministic routing.
    """

    @staticmethod
    def route(request: GatewayRequest) -> tuple[str, str]:
        """
        Determines the (provider_name, model_name) to use.
        """
        # If request explicitly specifies both, trust it
        if request.provider and request.model:
            return request.provider, request.model

        # If request specifies model but no provider, we do simple matching
        # In V1 we assume default provider if not obvious
        if request.model and not request.provider:
            # Simple heuristic: if it looks like Claude, use anthropic (future), etc.
            # For now, default to the default_provider
            return settings.default_provider, request.model

        # If no model specified, use system defaults
        return settings.default_provider, settings.default_model

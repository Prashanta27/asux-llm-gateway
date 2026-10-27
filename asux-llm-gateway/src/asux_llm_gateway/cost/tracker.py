from asux_llm_gateway.config import settings
from asux_llm_gateway.cost.pricing import get_pricing
from asux_llm_gateway.models.usage import TokenUsage


class CostTracker:
    """
    Calculates estimated costs for LLM requests based on token usage.
    """

    @staticmethod
    def calculate_cost(model: str, usage: TokenUsage | None) -> float | None:
        """
        Calculates the estimated cost in USD for a given usage.
        Returns None if usage is missing or cost tracking is disabled.
        """
        if not settings.enable_cost_tracking or usage is None:
            return None

        prompt_cost_per_1k, completion_cost_per_1k = get_pricing(model)

        prompt_cost = 0.0
        if usage.prompt_tokens and prompt_cost_per_1k > 0:
            prompt_cost = (usage.prompt_tokens / 1000.0) * prompt_cost_per_1k

        completion_cost = 0.0
        if usage.completion_tokens and completion_cost_per_1k > 0:
            completion_cost = (usage.completion_tokens / 1000.0) * completion_cost_per_1k

        total_cost = prompt_cost + completion_cost

        if total_cost == 0.0 and (usage.prompt_tokens or usage.completion_tokens):
            # We don't have pricing for this model, but we had usage
            return None

        return total_cost

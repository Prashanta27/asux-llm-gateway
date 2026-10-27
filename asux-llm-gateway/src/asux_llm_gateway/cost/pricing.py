# Simple static pricing table (cost per 1k tokens)
# In a real system this might be loaded from a DB or external service.
PRICING_TABLE: dict[str, tuple[float, float]] = {
    # model_name: (prompt_cost_per_1k, completion_cost_per_1k)
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4o": (0.005, 0.015),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-3.5-turbo": (0.0005, 0.0015),
    "claude-3-opus-20240229": (0.015, 0.075),
    "claude-3-sonnet-20240229": (0.003, 0.015),
    "claude-3-haiku-20240307": (0.00025, 0.00125),
}


def get_pricing(model: str) -> tuple[float, float]:
    """
    Returns (prompt_cost_per_1k, completion_cost_per_1k) for a given model.
    Falls back to (0.0, 0.0) if model is unknown.
    """
    # Sort keys by length descending to match most specific prefix first
    sorted_keys = sorted(PRICING_TABLE.keys(), key=len, reverse=True)

    for key in sorted_keys:
        if model.startswith(key):
            return PRICING_TABLE[key]

    return 0.0, 0.0

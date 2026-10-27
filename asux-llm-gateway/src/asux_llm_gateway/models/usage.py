from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """
    Standardized token usage tracking.
    """

    prompt_tokens: int | None = Field(
        default=None, description="Number of tokens in the input prompt."
    )
    completion_tokens: int | None = Field(
        default=None, description="Number of tokens generated in the completion."
    )
    total_tokens: int | None = Field(
        default=None, description="Total tokens used (prompt + completion)."
    )

    def add(self, other: "TokenUsage") -> "TokenUsage":
        """
        Combine this usage with another usage instance.
        Useful for aggregating streaming chunks.
        """

        def _add_opt(a: int | None, b: int | None) -> int | None:
            if a is None and b is None:
                return None
            return (a or 0) + (b or 0)

        return TokenUsage(
            prompt_tokens=_add_opt(self.prompt_tokens, other.prompt_tokens),
            completion_tokens=_add_opt(self.completion_tokens, other.completion_tokens),
            total_tokens=_add_opt(self.total_tokens, other.total_tokens),
        )

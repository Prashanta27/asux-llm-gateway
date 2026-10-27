import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from asux_llm_gateway.config import settings
from asux_llm_gateway.exceptions.errors import (
    AuthenticationError,
    InvalidRequestError,
    ProviderError,
    RateLimitError,
    GatewayTimeoutError,
)
from asux_llm_gateway.observability.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class RetryPolicy:
    """
    Handles retries for provider API calls with exponential backoff.
    """

    # Exceptions that should NEVER be retried
    NON_RETRYABLE_EXCEPTIONS = (
        AuthenticationError,
        InvalidRequestError,
        # StructuredOutputError and others usually shouldn't be retried
        # unless specifically instructed.
    )

    @classmethod
    def should_retry(cls, exception: Exception) -> bool:
        """Determine if an exception is retryable."""
        if isinstance(exception, cls.NON_RETRYABLE_EXCEPTIONS):
            return False

        # RateLimits and Timeouts are explicitly retryable
        if isinstance(exception, (RateLimitError, GatewayTimeoutError)):
            return True

        # General provider errors might be 5xx (server errors), so we retry
        return bool(isinstance(exception, ProviderError))

    @classmethod
    async def execute_with_retry(
        cls, coro_func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
    ) -> T:
        """
        Executes a coroutine with retry logic.
        Note: For streams, this only protects the INITIAL connection/request.
        If a stream fails midway, it's generally NOT safe to blindly retry here.
        """
        max_retries = settings.retry_count
        backoff_factor = settings.retry_backoff_factor
        max_delay = settings.retry_max_delay

        attempt = 0
        while True:
            try:
                return await coro_func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                if attempt > max_retries or not cls.should_retry(e):
                    logger.error(
                        "Request failed and exhausted retries or is non-retryable",
                        error=str(e),
                        attempt=attempt,
                    )
                    raise

                # Calculate delay with exponential backoff
                delay = min(backoff_factor**attempt, max_delay)
                logger.warning(
                    "Request failed, retrying...", error=str(e), attempt=attempt, delay=delay
                )
                await asyncio.sleep(delay)

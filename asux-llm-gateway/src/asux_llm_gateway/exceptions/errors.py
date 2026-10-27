class GatewayError(Exception):
    """Base exception for all Gateway errors."""

    pass


class ConfigurationError(GatewayError):
    """Raised when the gateway is misconfigured."""

    pass


class ProviderError(GatewayError):
    """Raised when the underlying provider returns an error."""

    pass


class AuthenticationError(ProviderError):
    """Raised when provider authentication fails."""

    pass


class RateLimitError(ProviderError):
    """Raised when the provider rate limit is exceeded."""

    pass


class GatewayTimeoutError(GatewayError):
    """Raised when a request to the provider times out."""

    pass


class InvalidRequestError(GatewayError):
    """Raised when the request parameters are invalid."""

    pass


class ModelNotFoundError(GatewayError):
    """Raised when the requested model cannot be found or routed."""

    pass


class StructuredOutputError(GatewayError):
    """Raised when the provider fails to return valid structured output."""

    pass


class StreamingError(GatewayError):
    """Raised when an error occurs during a streaming response."""

    pass

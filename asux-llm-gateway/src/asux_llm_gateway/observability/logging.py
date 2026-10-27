import json
import logging
import uuid
from typing import Any

from asux_llm_gateway.config import settings

# Configure root logger based on settings
logging.basicConfig(
    level=settings.log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class StructuredLogger:
    """
    A simple structured logger that writes JSON logs if desired, or standard text
    logs with structured kwargs appended.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def generate_request_id(self) -> str:
        return str(uuid.uuid4())

    def _log(self, level: int, msg: str, **kwargs: Any) -> None:
        if not self.logger.isEnabledFor(level):
            return

        if kwargs:
            # Mask sensitive things if they accidentally slipped in, though
            # we should prevent them at the source.
            safe_kwargs = {
                k: v
                for k, v in kwargs.items()
                if "api_key" not in k.lower() and "secret" not in k.lower()
            }
            msg = f"{msg} | {json.dumps(safe_kwargs, default=str)}"

        self.logger.log(level, msg)

    def debug(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, msg, **kwargs)

    def info(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, **kwargs)

    def exception(self, msg: str, **kwargs: Any) -> None:
        self.logger.exception(msg)
        if kwargs:
            self._log(logging.ERROR, "Exception context", **kwargs)


def get_logger(name: str) -> StructuredLogger:
    return StructuredLogger(name)

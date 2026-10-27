from enum import StrEnum

from pydantic import BaseModel


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ToolCall(BaseModel):
    """Represents a tool call from the assistant."""

    id: str
    type: str = "function"
    name: str
    arguments: str  # Usually JSON string


class Message(BaseModel):
    """
    Standardized message format for LLM requests.
    """

    role: MessageRole
    content: str | None = None

    # Optional fields for tool interactions
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None
    name: str | None = None

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role=MessageRole.SYSTEM, content=content)

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(role=MessageRole.USER, content=content)

    @classmethod
    def assistant(
        cls, content: str | None = None, tool_calls: list[ToolCall] | None = None
    ) -> "Message":
        return cls(role=MessageRole.ASSISTANT, content=content, tool_calls=tool_calls)

    @classmethod
    def tool(cls, content: str, tool_call_id: str, name: str) -> "Message":
        return cls(role=MessageRole.TOOL, content=content, tool_call_id=tool_call_id, name=name)

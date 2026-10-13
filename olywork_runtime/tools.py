"""Vendor-neutral tool registration and dispatch for the independent runtime."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import re

_NAME = re.compile(r"^[a-z][a-z0-9._-]{1,127}$")


class ToolDefinitionError(ValueError):
    """Raised when a tool does not satisfy the public contract."""


class ToolNotFound(LookupError):
    """Raised when a requested tool is not registered."""


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    handler: Callable[[Mapping[str, object]], object]
    input_schema: Mapping[str, object] = field(default_factory=lambda: {"type": "object"})


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if not _NAME.fullmatch(tool.name):
            raise ToolDefinitionError("tool name has invalid format")
        if not tool.description.strip():
            raise ToolDefinitionError("tool description is required")
        if tool.name in self._tools:
            raise ToolDefinitionError("tool name is already registered")
        self._tools[tool.name] = tool

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    def tools(self) -> tuple[Tool, ...]:
        return tuple(self._tools[name] for name in self.names())

    def invoke(self, name: str, arguments: Mapping[str, object]) -> object:
        tool = self._tools.get(name)
        if tool is None:
            raise ToolNotFound(name)
        return tool.handler(arguments)

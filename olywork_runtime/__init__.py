"""Independent runtime primitives for the Option A self-host implementation."""

from .auth import AuthenticationError, authenticate, bearer_token, static_verifier
from .http import application
from .mcp import handle
from .relay import RelayRequest, RelayResponse, relay
from .ssrf import UnsafeTarget, validate_target
from .tools import Tool, ToolDefinitionError, ToolNotFound, ToolRegistry

__all__ = [
    "AuthenticationError", "RelayRequest", "RelayResponse", "UnsafeTarget",
    "authenticate", "bearer_token", "relay", "static_verifier", "validate_target",
    "application",
    "handle",
    "Tool", "ToolDefinitionError", "ToolNotFound", "ToolRegistry",
]

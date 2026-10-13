"""Small MCP-shaped JSON-RPC dispatcher for the independent runtime."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .tools import ToolNotFound, ToolRegistry


def _error(request_id: object, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle(message: Mapping[str, Any], registry: ToolRegistry) -> dict[str, Any] | None:
    """Handle one JSON-RPC message; notifications return ``None``."""

    request_id = message.get("id")
    if message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
        return _error(request_id, -32600, "invalid request")
    method = message["method"]
    params = message.get("params") or {}
    if not isinstance(params, Mapping):
        return _error(request_id, -32602, "invalid params")

    if method == "initialize":
        result = {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "olywork-runtime", "version": "0.1.0"},
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        result = {
            "tools": [
                {"name": tool.name, "description": tool.description, "inputSchema": dict(tool.input_schema)}
                for tool in registry.tools()
            ]
        }
    elif method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        if not isinstance(name, str) or not isinstance(arguments, Mapping):
            return _error(request_id, -32602, "invalid params")
        try:
            result = {"content": [{"type": "text", "text": str(registry.invoke(name, arguments))}]}
        except ToolNotFound:
            return _error(request_id, -32602, "unknown tool")
    else:
        return _error(request_id, -32601, "method not found")

    if "id" not in message:
        return None
    return {"jsonrpc": "2.0", "id": request_id, "result": result}

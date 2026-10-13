"""Minimal WSGI adapter for the independent runtime contract."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from typing import Any

from .auth import AuthenticationError, authenticate
from .tools import ToolNotFound, ToolRegistry


def _json(status: str, payload: dict[str, Any], start_response: Callable[..., object]) -> list[bytes]:
    body = json.dumps(payload, separators=(",", ":")).encode()
    start_response(status, [("Content-Type", "application/json"), ("Content-Length", str(len(body)))])
    return [body]


def application(registry: ToolRegistry, verifier: Callable[[str], bool]) -> Callable[..., Iterable[bytes]]:
    """Build a WSGI application for a registry and caller-supplied token verifier."""

    def app(environ: dict[str, Any], start_response: Callable[..., object]) -> list[bytes]:
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/")
        if method == "GET" and path == "/health":
            return _json("200 OK", {"ok": True}, start_response)
        try:
            authenticate(environ, verifier)
        except AuthenticationError as error:
            return _json("401 Unauthorized", {"error": str(error)}, start_response)

        if method == "GET" and path == "/tools":
            return _json("200 OK", {"tools": list(registry.names())}, start_response)
        if method == "POST" and path == "/call":
            try:
                length = int(environ.get("CONTENT_LENGTH") or 0)
                payload = json.loads(environ["wsgi.input"].read(length) or b"{}")
                result = registry.invoke(payload["name"], payload.get("arguments", {}))
            except ToolNotFound:
                return _json("404 Not Found", {"error": "tool not found"}, start_response)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                return _json("400 Bad Request", {"error": "invalid call"}, start_response)
            return _json("200 OK", {"result": result}, start_response)
        return _json("404 Not Found", {"error": "not found"}, start_response)

    return app

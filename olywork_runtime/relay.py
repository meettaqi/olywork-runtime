"""A vendor-neutral HTTP relay.

The relay accepts a complete request description and does not inspect or reshape an upstream
payload. Authentication injection is explicit at the boundary and transport-only headers are
removed before sending.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .ssrf import validate_target

_HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
        "host",
        "content-length",
    }
)


@dataclass(frozen=True)
class RelayRequest:
    method: str
    url: str
    headers: dict[str, str]
    body: bytes = b""
    timeout_seconds: float = 30.0


@dataclass(frozen=True)
class RelayResponse:
    status: int
    headers: dict[str, str]
    body: bytes


def relay(request: RelayRequest, *, injected_headers: dict[str, str] | None = None) -> RelayResponse:
    """Send one request and return the upstream response without modeling its body."""

    validate_target(request.url)
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in _HOP_BY_HOP
    }
    for key, value in (injected_headers or {}).items():
        if key.lower() not in _HOP_BY_HOP:
            headers[key] = value

    outgoing = Request(
        request.url,
        data=request.body or None,
        headers=headers,
        method=request.method.upper(),
    )
    try:
        with urlopen(outgoing, timeout=request.timeout_seconds) as response:
            return RelayResponse(
                status=response.status,
                headers=dict(response.headers.items()),
                body=response.read(),
            )
    except HTTPError as error:
        return RelayResponse(
            status=error.code,
            headers=dict(error.headers.items()),
            body=error.read(),
        )
    except URLError:
        raise

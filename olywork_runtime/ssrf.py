"""Small, fail-closed target checks for the independent runtime."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class UnsafeTarget(ValueError):
    """Raised when a URL points at a non-public or unsupported target."""


def validate_target(url: str) -> None:
    """Reject schemes, host forms, and resolved addresses unsafe for server-side fetching."""

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeTarget("only http and https targets are supported")
    if not parsed.hostname or parsed.username or parsed.password:
        raise UnsafeTarget("target must contain a hostname without embedded credentials")

    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise UnsafeTarget("local hostnames are not allowed")

    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        if not literal.is_global:
            raise UnsafeTarget("non-public IP addresses are not allowed")
        return

    try:
        addresses = {
            info[4][0]
            for info in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
        }
    except (OSError, ValueError) as error:
        raise UnsafeTarget("hostname could not be resolved") from error
    if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise UnsafeTarget("hostname resolves to a non-public address")

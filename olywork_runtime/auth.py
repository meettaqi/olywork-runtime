"""Authentication primitives for a self-host deployment.

The runtime receives a verifier callback so deployments can choose their own secret store. No
tokens are persisted here and no hosted identity assumptions are made.
"""

from __future__ import annotations

import hmac
from collections.abc import Callable, Mapping


class AuthenticationError(ValueError):
    """Raised when a request does not contain an acceptable bearer token."""


def bearer_token(headers: Mapping[str, str]) -> str:
    value = next((v for k, v in headers.items() if k.lower() == "authorization"), "")
    scheme, separator, token = value.partition(" ")
    if not separator or scheme.lower() != "bearer" or not token:
        raise AuthenticationError("a bearer token is required")
    return token.strip()


def authenticate(
    headers: Mapping[str, str],
    verifier: Callable[[str], bool],
) -> None:
    """Validate a bearer token without exposing the token to logs or exceptions."""

    token = bearer_token(headers)
    if not verifier(token):
        raise AuthenticationError("invalid bearer token")


def static_verifier(expected: str) -> Callable[[str], bool]:
    """Return a constant-time verifier for local development only."""

    if not expected:
        raise ValueError("an expected token is required")

    def verify(candidate: str) -> bool:
        return hmac.compare_digest(candidate.encode(), expected.encode())

    return verify
